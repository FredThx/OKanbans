git pull
#Build and run API OKANBAN
sudo docker build --pull --rm -f api_Dockerfile -t api_okanbans:latest '.'
sudo docker stop api_okanbans
sudo docker rm api_okanbans
sudo docker run --env=GPG_KEY=A035C8C19219BA821ECEA86B64E628F8D684696D \
                --env=PYTHON_VERSION=3.10.18 \
                --env=PYTHON_SHA256=ae665bc678abd9ab6a6e1573d2481625a53719bc517e9a634ed2b9fefae3817f \
                --env=OKANBAN_CONSOLE_LEVEL=INFO \
                --env=OKANBAN_LOGFILE_LEVEL=INFO \
                --env=OKANBAN_MONGODB_HOST=192.168.0.20 \
                --env=OKANBAN_MONGODB_PORT=27017 \
                --env=OKANBAN_NICELABEL_URL=http://192.168.0.16:56425 \
                --env=OKANBAN_API_USERNAME=olfa \
                --env=OKANBAN_API_PASSWORD=Trone08 \
                --env=OKANBAN_ETIQUETTE=ET_PER_API \
                --network=bridge \
                -p 50890:50890 \
                --restart=no \
                --runtime=runc \
                --name=api_okanbans \
                -d api_okanbans:latest
# Clean up unused images
sudo docker image prune -f