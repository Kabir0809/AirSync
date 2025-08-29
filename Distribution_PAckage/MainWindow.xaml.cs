using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Threading;
using MaterialDesignThemes.Wpf;
using System.Threading.Tasks;
using System.Linq;

namespace AirSync
{
    public partial class MainWindow : Window
    {
        private Process? _pythonProcess;
        private bool _isRunning = false;
        private DispatcherTimer _statusTimer = null!;
        private StringBuilder _logBuffer = new StringBuilder();
        private GameManager _gameManager = null!;

    // Add references to UI controls if not auto-generated
        // private TextBlock FpsDisplay => (TextBlock)FindName("FpsDisplay");
        // private TextBlock StatusText => (TextBlock)FindName("StatusText");
        // private TextBlock StatusDetails => (TextBlock)FindName("StatusDetails");
        // private PackIcon StatusIcon => (PackIcon)FindName("StatusIcon");        // private PackIcon PythonIcon => (PackIcon)FindName("PythonIcon");
        // private PackIcon CameraIcon => (PackIcon)FindName("CameraIcon");
        // private PackIcon DependenciesIcon => (PackIcon)FindName("DependenciesIcon");
        // private TextBox LogOutput => (TextBox)FindName("LogOutput");
        // private ScrollViewer LogScrollViewer => (ScrollViewer)FindName("LogScrollViewer");

        public MainWindow()
        {
            InitializeComponent();
            InitializeApplication();
        }

        private void InitializeApplication()
        {
            // Initialize GameManager
            _gameManager = new GameManager();

            // Initialize status timer for UI updates
            _statusTimer = new DispatcherTimer
            {
                Interval = TimeSpan.FromSeconds(1)
            };
            _statusTimer.Tick += StatusTimer_Tick;
            _statusTimer.Start();

            // Check initial requirements
            CheckSystemRequirements();

            // Initialize game shortcuts
            InitializeGameShortcuts();

            // Add welcome message to log
            AddToLog("Welcome to AirSync - Hand Gesture Gaming Controller");
            AddToLog("Please ensure your webcam is connected and working properly.");
            AddToLog("Make sure you have Python 3.7+ installed with required dependencies.");
        }

        private async void InitializeGameShortcuts()
        {
            try
            {
                await _gameManager.LoadGamesAsync();
                UpdateGameShortcutsUI();
                AddToLog($"Loaded {_gameManager.Games.Count} game shortcuts.");
            }
            catch (Exception ex)
            {
                AddToLog($"Error loading game shortcuts: {ex.Message}");
            }
        }

        private void UpdateGameShortcutsUI()
        {
            // Update the ItemsControl with games
            if (FindName("GameShortcutsList") is ItemsControl gamesList)
            {
                gamesList.ItemsSource = _gameManager.Games;
            }
        }

        private void StatusTimer_Tick(object? sender, EventArgs e)
        {
            if (_isRunning && _pythonProcess != null && !_pythonProcess.HasExited)
            {
                // Update FPS display (placeholder - would need actual FPS from Python script)
                FpsDisplay.Text = "FPS: Active";
            }
            else if (_isRunning)
            {
                // Process has unexpectedly stopped
                StopApplication();
                AddToLog("⚠️ Python process stopped unexpectedly.");
            }
        }

        private void StartButton_Click(object sender, RoutedEventArgs e)
        {
            if (_isRunning) return;

            try
            {
                StartButton.IsEnabled = false;
                AddToLog("🚀 Starting AirSync hand gesture detection...");

                // Update UI to show starting state
                UpdateStatus("Starting...", "Initializing hand gesture detection", PackIconKind.Loading, "Orange");

                // Check if Python script exists
                string scriptPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "test.py");
                if (!File.Exists(scriptPath))
                {
                    throw new FileNotFoundException($"Python script not found at: {scriptPath}");
                }

                // Start Python process
                var startInfo = new ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = $"\"{scriptPath}\"",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                    WorkingDirectory = AppDomain.CurrentDomain.BaseDirectory
                };

                _pythonProcess = new Process { StartInfo = startInfo };

                // Set up output handling
                _pythonProcess.OutputDataReceived += (s, args) =>
                {
                    if (!string.IsNullOrEmpty(args.Data))
                    {
                        Dispatcher.Invoke(() => AddToLog($"📊 {args.Data}"));
                    }
                };

                _pythonProcess.ErrorDataReceived += (s, args) =>
                {
                    if (!string.IsNullOrEmpty(args.Data))
                    {
                        Dispatcher.Invoke(() => AddToLog($"❌ Error: {args.Data}"));
                    }
                };

                _pythonProcess.Exited += (s, args) =>
                {
                    Dispatcher.Invoke(() =>
                    {
                        if (_isRunning)
                        {
                            StopApplication();
                            AddToLog("🛑 Python process has exited.");
                        }
                    });
                };

                _pythonProcess.EnableRaisingEvents = true;

                // Start the process
                if (_pythonProcess.Start())
                {
                    _pythonProcess.BeginOutputReadLine();
                    _pythonProcess.BeginErrorReadLine();

                    _isRunning = true;
                    UpdateStatus("Running", "Hand gesture detection is active", PackIconKind.CheckCircle, "Green");

                    StartButton.IsEnabled = false;
                    StopButton.IsEnabled = true;

                    AddToLog("✅ AirSync started successfully!");
                    AddToLog("📹 Calibration will begin - follow on-screen instructions");
                    AddToLog("🎮 Ready to control your racing games with hand gestures!");
                }
                else
                {
                    throw new Exception("Failed to start Python process");
                }
            }
            catch (Exception ex)
            {
                AddToLog($"❌ Failed to start: {ex.Message}");
                UpdateStatus("Error", $"Failed to start: {ex.Message}", PackIconKind.AlertCircle, "Red");
                StartButton.IsEnabled = true;
            }
        }

        private void StopButton_Click(object sender, RoutedEventArgs e)
        {
            StopApplication();
        }

        private void StopApplication()
        {
            if (_pythonProcess != null && !_pythonProcess.HasExited)
            {
                try
                {
                    AddToLog("🛑 Stopping AirSync...");

                    // Try graceful shutdown first
                    _pythonProcess.CloseMainWindow();

                    // Wait a bit for graceful shutdown
                    if (!_pythonProcess.WaitForExit(3000))
                    {
                        // Force kill if necessary
                        _pythonProcess.Kill();
                        AddToLog("⚠️ Process force terminated");
                    }
                }
                catch (Exception ex)
                {
                    AddToLog($"⚠️ Error stopping process: {ex.Message}");
                }
                finally
                {
                    _pythonProcess.Dispose();
                    _pythonProcess = null;
                }
            }

            _isRunning = false;
            UpdateStatus("Stopped", "Hand gesture detection stopped", PackIconKind.StopCircle, "Orange");

            StartButton.IsEnabled = true;
            StopButton.IsEnabled = false;
            FpsDisplay.Text = "FPS: --";

            AddToLog("✅ AirSync stopped successfully");
        }

        private async void CheckDependencies_Click(object sender, RoutedEventArgs e)
        {
            AddToLog("🔍 Checking Python dependencies...");

            try
            {
                var process = new Process
                {
                    StartInfo = new ProcessStartInfo
                    {
                        FileName = "python",
                        Arguments = "-c \"import cv2, mediapipe, numpy, vgamepad; print('All dependencies are installed!')\"",
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true
                    }
                };

                process.Start();
                string output = await process.StandardOutput.ReadToEndAsync();
                string error = await process.StandardError.ReadToEndAsync();
                await process.WaitForExitAsync();

                if (process.ExitCode == 0)
                {
                    AddToLog("✅ All Python dependencies are properly installed!");
                    UpdateDependencyStatus(true);
                }
                else
                {
                    AddToLog($"❌ Missing dependencies: {error}");
                    UpdateDependencyStatus(false);
                }
            }
            catch (Exception ex)
            {
                AddToLog($"❌ Error checking dependencies: {ex.Message}");
                UpdateDependencyStatus(false);
            }
        }

        private async void InstallDependencies_Click(object sender, RoutedEventArgs e)
        {
            AddToLog("📦 Installing Python dependencies...");
            AddToLog("This may take a few minutes...");

            try
            {
                string requirementsPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "requirements.txt");

                var process = new Process
                {
                    StartInfo = new ProcessStartInfo
                    {
                        FileName = "python",
                        Arguments = $"-m pip install -r \"{requirementsPath}\"",
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true
                    }
                };

                process.OutputDataReceived += (s, args) =>
                {
                    if (!string.IsNullOrEmpty(args.Data))
                    {
                        Dispatcher.Invoke(() => AddToLog($"📦 {args.Data}"));
                    }
                };

                process.Start();
                process.BeginOutputReadLine();
                await process.WaitForExitAsync();

                if (process.ExitCode == 0)
                {
                    AddToLog("✅ Dependencies installed successfully!");
                    CheckSystemRequirements();
                }
                else
                {
                    AddToLog("❌ Failed to install some dependencies. Check the log for details.");
                }
            }
            catch (Exception ex)
            {
                AddToLog($"❌ Error installing dependencies: {ex.Message}");
            }
        }

        private void ShowAbout_Click(object sender, RoutedEventArgs e)
        {
            var aboutDialog = new AboutDialog();
            aboutDialog.ShowDialog();
        }

        private void ClearLog_Click(object sender, RoutedEventArgs e)
        {
            LogOutput.Text = "";
            _logBuffer.Clear();
            AddToLog("📝 Log cleared");
        }

        private void CheckSystemRequirements()
        {
            // Check Python
            CheckPython();

            // Check camera (basic check)
            CheckCamera();
        }

        private async void CheckPython()
        {
            try
            {
                var process = new Process
                {
                    StartInfo = new ProcessStartInfo
                    {
                        FileName = "python",
                        Arguments = "--version",
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true
                    }
                };

                process.Start();
                string output = await process.StandardOutput.ReadToEndAsync();
                await process.WaitForExitAsync();

                if (process.ExitCode == 0 && output.Contains("Python 3."))
                {
                    PythonIcon.Kind = PackIconKind.CheckCircle;
                    PythonIcon.Foreground = System.Windows.Media.Brushes.Green;
                    AddToLog($"✅ {output.Trim()} detected");
                }
                else
                {
                    PythonIcon.Kind = PackIconKind.AlertCircle;
                    PythonIcon.Foreground = System.Windows.Media.Brushes.Red;
                    AddToLog("❌ Python 3.7+ not found. Please install Python.");
                }
            }
            catch
            {
                PythonIcon.Kind = PackIconKind.AlertCircle;
                PythonIcon.Foreground = System.Windows.Media.Brushes.Red;
                AddToLog("❌ Python not found in PATH. Please install Python.");
            }
        }

        private void CheckCamera()
        {
            // This is a basic check - the actual camera test happens in the Python script
            CameraIcon.Kind = PackIconKind.CheckCircle;
            CameraIcon.Foreground = System.Windows.Media.Brushes.Orange;
            AddToLog("📹 Camera check will be performed when starting detection");
        }

        private void UpdateDependencyStatus(bool allInstalled)
        {
            if (allInstalled)
            {
                DependenciesIcon.Kind = PackIconKind.CheckCircle;
                DependenciesIcon.Foreground = System.Windows.Media.Brushes.Green;
            }
            else
            {
                DependenciesIcon.Kind = PackIconKind.AlertCircle;
                DependenciesIcon.Foreground = System.Windows.Media.Brushes.Red;
            }
        }

        private void UpdateStatus(string status, string details, PackIconKind icon, string color)
        {
            StatusText.Text = status;
            StatusDetails.Text = details;
            StatusIcon.Kind = icon;

            var brush = color switch
            {
                "Green" => System.Windows.Media.Brushes.Green,
                "Red" => System.Windows.Media.Brushes.Red,
                "Orange" => System.Windows.Media.Brushes.Orange,
                _ => System.Windows.Media.Brushes.Gray
            };
            StatusIcon.Foreground = brush;
        }

        private void AddToLog(string message)
        {
            var timestamp = DateTime.Now.ToString("HH:mm:ss");
            var logLine = $"[{timestamp}] {message}";

            _logBuffer.AppendLine(logLine);
            LogOutput.Text = _logBuffer.ToString();

            // Auto-scroll to bottom
            LogScrollViewer.ScrollToEnd();
        }

        protected override void OnClosing(System.ComponentModel.CancelEventArgs e)
        {
            if (_isRunning)
            {
                StopApplication();
            }
            _statusTimer?.Stop();
            base.OnClosing(e);
        }

        // Game Shortcuts Event Handlers
        private void AddGame_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var dialog = new AddEditGameDialog(_gameManager);
                dialog.Owner = this;
                dialog.ShowDialog();

                if (dialog.DialogResult == true)
                {
                    UpdateGameShortcutsUI();
                    AddToLog($"Added game: {dialog.GameShortcut.Name}");
                }
            }
            catch (Exception ex)
            {
                AddToLog($"Error adding game: {ex.Message}");
                MessageBox.Show($"Error adding game: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void ManageGames_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // For now, just show a message with game count
                var message = $"You have {_gameManager.Games.Count} games configured.\n\n";
                message += "Use the individual game buttons to launch, edit, or delete games.";

                MessageBox.Show(message, "Game Management", MessageBoxButton.OK, MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                AddToLog($"Error managing games: {ex.Message}");
                MessageBox.Show($"Error managing games: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private async void LaunchGame_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (sender is Button button && button.Tag is GameShortcut game)
                {
                    AddToLog($"Launching game: {game.Name}");

                    // Run test.py before launching the game, and track the process
                    try
                    {
                        string pythonExe = "python";
                        string scriptPath = System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "test.py");
                        var psi = new System.Diagnostics.ProcessStartInfo
                        {
                            FileName = pythonExe,
                            Arguments = $"\"{scriptPath}\"",
                            UseShellExecute = false,
                            CreateNoWindow = true,
                            RedirectStandardOutput = true,
                            RedirectStandardError = true
                        };
                        _pythonProcess = System.Diagnostics.Process.Start(psi);
                        AddToLog("Started hand gesture recognition script (test.py)");
                        StopButton.IsEnabled = true;
                        StartButton.IsEnabled = false;
                        await Task.Delay(1000); // Let the script start
                    }
                    catch (Exception pyEx)
                    {
                        AddToLog($"Failed to start test.py: {pyEx.Message}");
                        MessageBox.Show($"Failed to start hand gesture recognition script: {pyEx.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                    }

                    var success = await _gameManager.LaunchGameAsync(game);
                    if (success)
                    {
                        AddToLog($"Successfully launched: {game.Name}");
                        UpdateGameShortcutsUI(); // Update play count and last played
                    }
                }
            }
            catch (Exception ex)
            {
                AddToLog($"Error launching game: {ex.Message}");
                MessageBox.Show($"Error launching game: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void EditGame_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (sender is Button button && button.Tag is GameShortcut game)
                {
                    var dialog = new AddEditGameDialog(_gameManager, game);
                    dialog.Owner = this;
                    dialog.ShowDialog();

                    if (dialog.DialogResult == true)
                    {
                        UpdateGameShortcutsUI();
                        AddToLog($"Updated game: {game.Name}");
                    }
                }
            }
            catch (Exception ex)
            {
                AddToLog($"Error editing game: {ex.Message}");
                MessageBox.Show($"Error editing game: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private async void DeleteGame_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (sender is Button button && button.Tag is GameShortcut game)
                {
                    var result = MessageBox.Show(
                        $"Are you sure you want to delete '{game.Name}'?\n\nThis action cannot be undone.",
                        "Delete Game",
                        MessageBoxButton.YesNo,
                        MessageBoxImage.Question);

                    if (result == MessageBoxResult.Yes)
                    {
                        await _gameManager.RemoveGameAsync(game);
                        UpdateGameShortcutsUI();
                        AddToLog($"Deleted game: {game.Name}");
                    }
                }
            }
            catch (Exception ex)
            {
                AddToLog($"Error deleting game: {ex.Message}");
                MessageBox.Show($"Error deleting game: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }
    }
}
