using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;
using System.Linq;

namespace AirSync
{
    /// <summary>
    /// Manages game shortcuts including loading, saving, and launching games
    /// </summary>
    public class GameManager
    {
        private const string GAMES_FILE = "games.json";
        private readonly string _gamesFilePath;

        public ObservableCollection<GameShortcut> Games { get; private set; }

        public GameManager()
        {
            Games = new ObservableCollection<GameShortcut>();
            _gamesFilePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, GAMES_FILE);
        }

        /// <summary>
        /// Load games from the JSON file
        /// </summary>
        public async Task LoadGamesAsync()
        {
            try
            {
                if (!File.Exists(_gamesFilePath))
                {
                    // Create default games file with some popular racing games
                    await CreateDefaultGamesAsync();
                    return;
                }

                var json = await File.ReadAllTextAsync(_gamesFilePath);
                var games = JsonSerializer.Deserialize<GameShortcut[]>(json);

                Games.Clear();
                if (games != null)
                {
                    foreach (var game in games)
                    {
                        Games.Add(game);
                    }
                }
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to load games: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Save games to the JSON file
        /// </summary>
        public async Task SaveGamesAsync()
        {
            try
            {
                var json = JsonSerializer.Serialize(Games.ToArray(), new JsonSerializerOptions
                {
                    WriteIndented = true
                });

                await File.WriteAllTextAsync(_gamesFilePath, json);
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to save games: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Add a new game shortcut
        /// </summary>
        public async Task AddGameAsync(GameShortcut game)
        {
            if (game == null) throw new ArgumentNullException(nameof(game));

            // Check for duplicate names
            if (Games.Any(g => g.Name.Equals(game.Name, StringComparison.OrdinalIgnoreCase)))
            {
                throw new InvalidOperationException("A game with this name already exists.");
            }

            Games.Add(game);
            await SaveGamesAsync();
        }

        /// <summary>
        /// Update an existing game shortcut
        /// </summary>
        public async Task UpdateGameAsync(GameShortcut game)
        {
            if (game == null) throw new ArgumentNullException(nameof(game));

            var existingGame = Games.FirstOrDefault(g => g.Id == game.Id);
            if (existingGame == null)
            {
                throw new InvalidOperationException("Game not found.");
            }

            // Check for duplicate names (excluding current game)
            if (Games.Any(g => g.Id != game.Id && g.Name.Equals(game.Name, StringComparison.OrdinalIgnoreCase)))
            {
                throw new InvalidOperationException("A game with this name already exists.");
            }

            existingGame.Name = game.Name;
            existingGame.Path = game.Path;
            existingGame.Arguments = game.Arguments;

            await SaveGamesAsync();
        }

        /// <summary>
        /// Remove a game shortcut
        /// </summary>
        public async Task RemoveGameAsync(GameShortcut game)
        {
            if (game == null) throw new ArgumentNullException(nameof(game));

            Games.Remove(game);
            await SaveGamesAsync();
        }

        /// <summary>
        /// Launch a game
        /// </summary>
        public async Task<bool> LaunchGameAsync(GameShortcut game)
        {
            if (game == null) throw new ArgumentNullException(nameof(game));

            if (!game.IsValid)
            {
                throw new FileNotFoundException($"Game executable not found: {game.Path}");
            }

            try
            {
                var startInfo = new ProcessStartInfo
                {
                    FileName = game.Path,
                    Arguments = game.Arguments ?? string.Empty,
                    UseShellExecute = true,
                    WorkingDirectory = Path.GetDirectoryName(game.Path)
                };

                Process.Start(startInfo);

                // Update play statistics
                game.LastPlayed = DateTime.Now;
                game.PlayCount++;

                await SaveGamesAsync();
                return true;
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to launch game '{game.Name}': {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Create default games file with common racing game paths
        /// </summary>
        private async Task CreateDefaultGamesAsync()
        {
            var defaultGames = new[]
            {
                new GameShortcut
                {
                    Name = "Example Racing Game",
                    Path = @"C:\Program Files\Example\RacingGame.exe",
                    Arguments = ""
                }
            };

            foreach (var game in defaultGames)
            {
                Games.Add(game);
            }

            await SaveGamesAsync();
        }

        /// <summary>
        /// Auto-detect popular racing games installed on the system
        /// </summary>
        public async Task<GameShortcut[]> DetectInstalledGamesAsync()
        {
            var detectedGames = new List<GameShortcut>();

            // Common racing game installation paths
            var commonPaths = new[]
            {
                @"C:\Program Files (x86)\Steam\steamapps\common",
                @"C:\Program Files\Steam\steamapps\common",
                @"C:\Program Files (x86)\Epic Games",
                @"C:\Program Files\Epic Games",
                @"C:\Program Files (x86)\Origin Games",
                @"C:\Program Files\Origin Games",
                @"C:\Program Files (x86)\EA Games",
                @"C:\Program Files\EA Games"
            };

            // Common racing game executable patterns
            var gamePatterns = new Dictionary<string, string[]>
            {
                { "Forza Horizon", new[] { "*ForzaHorizon*.exe" } },
                { "Forza Motorsport", new[] { "*ForzaMotorsport*.exe" } },
                { "Need for Speed", new[] { "*NeedForSpeed*.exe", "*NFS*.exe" } },
                { "F1", new[] { "*F1_*.exe", "*F1*.exe" } },
                { "Dirt Rally", new[] { "*DirtRally*.exe", "*dirt*.exe" } },
                { "Gran Turismo", new[] { "*GranTurismo*.exe", "*GT*.exe" } },
                { "Assetto Corsa", new[] { "*AssettoCorsa*.exe", "*acs*.exe" } },
                { "Project CARS", new[] { "*pCARS*.exe", "*ProjectCARS*.exe" } },
                { "Burnout", new[] { "*Burnout*.exe" } },
                { "The Crew", new[] { "*TheCrew*.exe" } }
            };

            await Task.Run(() =>
            {
                foreach (var basePath in commonPaths)
                {
                    if (!Directory.Exists(basePath)) continue;

                    try
                    {
                        var directories = Directory.GetDirectories(basePath);
                        foreach (var directory in directories)
                        {
                            foreach (var gamePattern in gamePatterns)
                            {
                                foreach (var pattern in gamePattern.Value)
                                {
                                    try
                                    {
                                        var files = Directory.GetFiles(directory, pattern, SearchOption.TopDirectoryOnly);
                                        foreach (var file in files)
                                        {
                                            var gameName = gamePattern.Key;
                                            var directoryName = Path.GetFileName(directory);

                                            // Use directory name if it's more descriptive
                                            if (directoryName.Contains(gamePattern.Key, StringComparison.OrdinalIgnoreCase))
                                            {
                                                gameName = directoryName;
                                            }

                                            detectedGames.Add(new GameShortcut
                                            {
                                                Name = gameName,
                                                Path = file,
                                                Arguments = ""
                                            });
                                        }
                                    }
                                    catch
                                    {
                                        // Ignore errors for individual directories
                                    }
                                }
                            }
                        }
                    }
                    catch
                    {
                        // Ignore errors for individual base paths
                    }
                }
            });

            return detectedGames.ToArray();
        }
    }
}
