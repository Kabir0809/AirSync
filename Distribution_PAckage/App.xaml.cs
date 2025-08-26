using System.Windows;
using MaterialDesignThemes.Wpf;

namespace AirSync
{
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            // Set up Material Design theming
            var paletteHelper = new PaletteHelper();
            var theme = paletteHelper.GetTheme();

            // Set dark base theme using the updated API
            theme.SetBaseTheme(Theme.Dark);

            paletteHelper.SetTheme(theme);
        }
    }
}
