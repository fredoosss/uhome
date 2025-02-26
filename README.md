# Uhome

The **U home** integration allows you to control [U home](https://u-tec.com/pages/u-home) devices.

U home is a platform from [U-tec](https://u-tec.com/) supporting [Ultraloq Smart Locks](https://u-tec.com/pages/ultraloq), [Ulticam Smart Cameras](https://u-tec.com/pages/ulticam), [Bright Smart Lighting](https://u-tec.com/pages/ulticam), and [U-tec Smart Power](https://u-tec.com/pages/ulticam) devices.

## Configuration

Ensure that [HACS](https://hacs.xyz/) is installed. Search for and add the U home integration.

During setup, you will be prompted for a name, client ID, and client secret. The name can be set to any value, for example, your U home username. The client ID and  client secret come from U-tec. See the [Authentication](#authentication) section for details.

## Authentication

> [!TIP]
> Install and set up the U home app before starting the following steps.

* Contact [U-tec Customer Service](https://support.u-tec.com/hc/en-us/requests/new) to request a Developer Account. Once your Developer Account is set up, the Developer Console menu option will appear in your U home app.
* From within the U home app, open the Developer Console
  * Note the `client_id` and `client_secret`, you will need these when setting up the U home integration.
  * Add `https://my.home-assistant.io/redirect/oauth` as an additional RedirectUri.
  * If your Home Assistant instance is available on the public internet, also include `https://{YOUR_DOMAIN_HERE}/auth/external/callback` as an additional RedirectUri.

## Options

Once set up, the poll interval can be specified in the U home Configuration options. The default is 5 minutes.

## Limitations

Currently, only Ultraloq Smart Locks are fully supported by this integration. Other device types will be recognized but can not be controlled.

## Disclaimer

This package and its author are not affiliated with U-tec. Use at your own risk.

## License

The package is released under the MIT license.
