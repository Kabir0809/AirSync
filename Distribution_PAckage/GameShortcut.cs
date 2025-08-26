using System;
using System.ComponentModel;
using System.IO;

namespace AirSync
{
    /// <summary>
    /// Represents a game shortcut with name, path, and display information
    /// </summary>
    public class GameShortcut : INotifyPropertyChanged
    {
        private string _name = string.Empty;
        private string _path = string.Empty;
        private string _arguments = string.Empty;
        private DateTime _lastPlayed;
        private int _playCount;

        /// <summary>
        /// Unique identifier for the game shortcut
        /// </summary>
        public Guid Id { get; set; } = Guid.NewGuid();

        /// <summary>
        /// Display name of the game
        /// </summary>
        public string Name
        {
            get => _name;
            set
            {
                _name = value;
                OnPropertyChanged(nameof(Name));
            }
        }

        /// <summary>
        /// Full path to the game executable
        /// </summary>
        public string Path
        {
            get => _path;
            set
            {
                _path = value;
                OnPropertyChanged(nameof(Path));
                OnPropertyChanged(nameof(DisplayPath));
                OnPropertyChanged(nameof(IsValid));
            }
        }

        /// <summary>
        /// Command line arguments for launching the game
        /// </summary>
        public string Arguments
        {
            get => _arguments;
            set
            {
                _arguments = value;
                OnPropertyChanged(nameof(Arguments));
            }
        }

        /// <summary>
        /// Last time the game was played
        /// </summary>
        public DateTime LastPlayed
        {
            get => _lastPlayed;
            set
            {
                _lastPlayed = value;
                OnPropertyChanged(nameof(LastPlayed));
                OnPropertyChanged(nameof(LastPlayedText));
            }
        }

        /// <summary>
        /// Number of times the game has been launched
        /// </summary>
        public int PlayCount
        {
            get => _playCount;
            set
            {
                _playCount = value;
                OnPropertyChanged(nameof(PlayCount));
            }
        }

        /// <summary>
        /// Display-friendly version of the path (filename only)
        /// </summary>
        public string DisplayPath
        {
            get
            {
                if (string.IsNullOrEmpty(Path))
                    return "No path specified";

                try
                {
                    return System.IO.Path.GetFileName(Path);
                }
                catch
                {
                    return Path;
                }
            }
        }

        /// <summary>
        /// Whether the game executable exists and is valid
        /// </summary>
        public bool IsValid
        {
            get
            {
                return !string.IsNullOrEmpty(Path) && File.Exists(Path);
            }
        }

        /// <summary>
        /// Display text for last played time
        /// </summary>
        public string LastPlayedText
        {
            get
            {
                if (LastPlayed == default)
                    return "Never played";

                var timeSpan = DateTime.Now - LastPlayed;
                if (timeSpan.TotalDays >= 1)
                    return $"{(int)timeSpan.TotalDays} days ago";
                else if (timeSpan.TotalHours >= 1)
                    return $"{(int)timeSpan.TotalHours} hours ago";
                else if (timeSpan.TotalMinutes >= 1)
                    return $"{(int)timeSpan.TotalMinutes} minutes ago";
                else
                    return "Just now";
            }
        }

        public event PropertyChangedEventHandler? PropertyChanged;

        protected virtual void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        /// <summary>
        /// Creates a copy of this game shortcut
        /// </summary>
        public GameShortcut Clone()
        {
            return new GameShortcut
            {
                Id = this.Id,
                Name = this.Name,
                Path = this.Path,
                Arguments = this.Arguments,
                LastPlayed = this.LastPlayed,
                PlayCount = this.PlayCount
            };
        }

        public override string ToString()
        {
            return $"{Name} ({DisplayPath})";
        }
    }
}
