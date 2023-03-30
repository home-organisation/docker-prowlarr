# Prowlarr
This docker image is a custom image of prowlarr based on lscr.io/linuxserver/prowlarr

This container is usable to configure :
- Prowlarr authentication (user, password, apikey)
- Prowlarr Indexer Proxy (FlareSolverr with tags flare)

## How to deploy Prowlarr
### Initialize your environment
Before deploy your Prowlarr instance, you have to generate **Secret** :
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: prowlarr-secret
data:
  PROWLARR_USER: *********
  PROWLARR_PASSWORD: *********
  PROWLARR_APIKEY: *********
type: Opaque
```
*prowlarr-secret need an encrypted password, check in database in table "Users" after GUI password set to retrieve it*

### Deploy Prowlarr with flareSolverr
```yaml
      containers:
        - image: quay.io/bizalu/prowlarr:latest
          imagePullPolicy: IfNotPresent
          name: prowlarr
          ports:
            - containerPort: 9696
              protocol: TCP
          env:
            - name: PGID
              value: "1000"
            - name: PUID
              value: "1000"
            - name: TZ
              value: "Europe/Paris"
          envFrom:
            - secretRef:
                name: prowlarr-secret
          volumeMounts:
            - name: prowlarr-config
              mountPath: /config
        - image: ghcr.io/flaresolverr/flaresolverr:latest
          imagePullPolicy: IfNotPresent
          name: flaresolverr
          ports:
            - name: web
              containerPort: 8191
              protocol: TCP
          env:
            - name: TZ
              value: "Europe/Paris"
            - name: CAPTCHA_SOLVER
              value: 'none'
```