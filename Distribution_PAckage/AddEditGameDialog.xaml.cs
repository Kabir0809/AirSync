using System;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using Microsoft.Win32;
using MaterialDesignThemes.Wpf;
using System.Linq;
using System.Collections.Generic;

namespace AirSync
{
    /// <summary>
    /// Interaction logic for AddEditGameDialog.xaml
    /// </summary>
    public partial class AddEditGameDialog : Window
    {
        private readonly GameManager _gameManager;
        private readonly GameShortcut _gameShortcut;
        private readonly bool _isEditMode;

        public GameShortcut GameShortcut => _gameShortcut;
        public new bool? DialogResult { get; private set; }

        public AddEditGameDialog(GameManager gameManager, GameShortcut? gameShortcut = null)
        {
            InitializeComponent();

            _gameManager = gameManager ?? throw new ArgumentNullException(nameof(gameManager));
            _isEditMode = gameShortcut != null;
            _gameShortcut = gameShortcut ?? new GameShortcut();

            InitializeDialog();
        }

        private void InitializeDialog()
        {
            // Set dialog title and icon based on mode
            if (_isEditMode)
            {
                Title = "Edit Game";
                HeaderText.Text = "Edit Game";
                HeaderIcon.Kind = PackIconKind.Edit;
                SaveButton.Content = "Update Game";
            }
            else
            {
                Title = "Add Game";
                HeaderText.Text = "Add New Game";
                HeaderIcon.Kind = PackIconKind.Plus;
                SaveButton.Content = "Add Game";
            }

            // Set data context for binding
            DataContext = _gameShortcut;

            // Hide detected games initially
            DetectedGamesScrollViewer.Visibility = Visibility.Collapsed;

            // Validate initial state
            ValidateForm();
        }

        private void BrowseGame_Click(object sender, RoutedEventArgs e)
        {
            var openFileDialog = new OpenFileDialog
            {
                Title = "Select Game Executable",
                Filter = "Executable files (*.exe)|*.exe|All files (*.*)|*.*",
                InitialDirectory = Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles)
            };

            if (openFileDialog.ShowDialog() == true)
            {
                GamePathTextBox.Text = openFileDialog.FileName;

                // Auto-fill game name if empty
                if (string.IsNullOrWhiteSpace(GameNameTextBox.Text))
                {
                    GameNameTextBox.Text = Path.GetFileNameWithoutExtension(openFileDialog.FileName);
                }
            }
        }

        private async void ScanGames_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // Show loading
                ScanningPanel.Visibility = Visibility.Visible;
                DetectedGamesScrollViewer.Visibility = Visibility.Collapsed;

                // Detect games
                var detectedGames = await _gameManager.DetectInstalledGamesAsync();

                // Filter out games that are already added
                var filteredGames = detectedGames.Where(g =>
                    !_gameManager.Games.Any(existing =>
                        existing.Name.Equals(g.Name, StringComparison.OrdinalIgnoreCase) ||
                        existing.Path.Equals(g.Path, StringComparison.OrdinalIgnoreCase)
                    )).ToList();

                // Show results
                DetectedGamesList.ItemsSource = filteredGames;

                if (filteredGames.Any())
                {
                    DetectedGamesScrollViewer.Visibility = Visibility.Visible;
                    ShowMessage($"Found {filteredGames.Count} games", false);
                }
                else
                {
                    ShowMessage("No new games detected", true);
                }
            }
            catch (Exception ex)
            {
                ShowMessage($"Error scanning games: {ex.Message}", true);
            }
            finally
            {
                ScanningPanel.Visibility = Visibility.Collapsed;
            }
        }

        private void UseDetectedGame_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.Tag is GameShortcut detectedGame)
            {
                GameNameTextBox.Text = detectedGame.Name;
                GamePathTextBox.Text = detectedGame.Path;
                ArgumentsTextBox.Text = detectedGame.Arguments;

                // Hide detected games list
                DetectedGamesScrollViewer.Visibility = Visibility.Collapsed;

                ShowMessage($"Selected: {detectedGame.Name}", false);
            }
        }

        private void GameNameTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            ValidateForm();
        }

        private void GamePathTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            ValidateForm();
        }

        private void ValidateForm()
        {
            var isValid = !string.IsNullOrWhiteSpace(GameNameTextBox.Text) &&
                         !string.IsNullOrWhiteSpace(GamePathTextBox.Text) &&
                         File.Exists(GamePathTextBox.Text?.Trim());

            SaveButton.IsEnabled = isValid;

            // Update validation message
            if (!isValid)
            {
                string message = "";
                if (string.IsNullOrWhiteSpace(GameNameTextBox.Text))
                {
                    message = "Game name is required.";
                }
                else if (string.IsNullOrWhiteSpace(GamePathTextBox.Text))
                {
                    message = "Game path is required.";
                }
                else if (!File.Exists(GamePathTextBox.Text?.Trim()))
                {
                    message = "Game executable not found.";
                }

                ShowValidationMessage(message);
            }
            else
            {
                ValidationPanel.Visibility = Visibility.Collapsed;
            }
        }

        private async void Save_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // Update the game shortcut properties
                _gameShortcut.Name = GameNameTextBox.Text?.Trim() ?? string.Empty;
                _gameShortcut.Path = GamePathTextBox.Text?.Trim() ?? string.Empty;
                _gameShortcut.Arguments = ArgumentsTextBox.Text?.Trim() ?? string.Empty;

                // Check for duplicate names (excluding current game in edit mode)
                if (_gameManager.Games.Any(g => g.Id != _gameShortcut.Id &&
                    g.Name.Equals(_gameShortcut.Name, StringComparison.OrdinalIgnoreCase)))
                {
                    ShowMessage("A game with this name already exists.", true);
                    return;
                }

                // Check if the file exists before adding
                if (!File.Exists(_gameShortcut.Path))
                {
                    ShowMessage($"The file '{_gameShortcut.Path}' does not exist. Please enter a valid executable path.", true);
                    return;
                }

                // Add or update the game in the manager
                if (_isEditMode)
                {
                    await _gameManager.UpdateGameAsync(_gameShortcut);
                }
                else
                {
                    await _gameManager.AddGameAsync(_gameShortcut);
                }

                // Ensure dialog result is set and window closes
                Dispatcher.Invoke(() =>
                {
                    DialogResult = true;
                    Close();
                });
            }
            catch (Exception ex)
            {
                ShowMessage($"Error saving game: {ex.Message}", true);
            }
        }

        private void Cancel_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
            Close();
        }

        private void ShowMessage(string message, bool isError)
        {
            try
            {
                // Simple message display - you can enhance this with Material Design snackbar
                MessageBox.Show(message, isError ? "Error" : "Information",
                    MessageBoxButton.OK, isError ? MessageBoxImage.Error : MessageBoxImage.Information);
            }
            catch
            {
                // Fallback - should not happen
            }
        }

        private void ShowValidationMessage(string message)
        {
            ValidationMessage.Text = message;
            ValidationPanel.Visibility = Visibility.Visible;
        }
    }
}
