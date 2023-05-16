# Prowlarr
This docker image is a custom image of prowlarr based on lscr.io/linuxserver/prowlarr.

# Parameters
Container images are configured using parameters passed at runtime has environment variable. 

The parameters below are taken from the original image [lscr.io/linuxserver/prowlarr](https://hub.docker.com/r/linuxserver/prowlarr) :
|  Parameters | Examples values  | Functions                                                                                                      |
|-------------|------------------|----------------------------------------------------------------------------------------------------------------|
| PUID        |  1000            | for UserID                                                                                                     |
| PGID        |  1000            | for GroupID                                                                                                    |
| TZ          |  Europe/Paris    | Specify a timezone to use, see this [List](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List). |


The extra parameters below come from this custom image :
|  Parameters          | Examples values        | Functions                                                                                 |
|----------------------|------------------------|-------------------------------------------------------------------------------------------|
| PROWLARR_AUTHMETHOD  |  Forms                 | Authentication method for web authentication. Acceptable value is **Forms** or **Basic**  |
| PROWLARR_USER        |  admin                 | Username for web authentication                                                           |
| PROWLARR_PASSWORD    |  ****                  | Password for web authentication                                                           |
| PROWLARR_APIKEY      |  ****                  | Key for api authentication                                                                |
| PROWLARR_PROXYURL    |  http://localhost:8191 | FlareSolverr Indexer Proxy URL                                                            |
| PROWLARR_PROXYNAME   |  FlareSolverr          | FlareSolverr Indexer Proxy name                                                           |
| PROWLARR_PROXYTAG    |  flare                 | FlareSolverr Indexer Proxy tag                                                            |
