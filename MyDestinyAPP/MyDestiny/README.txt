Comando para construir el contenedor:

docker build --no-cache --rm -t my_destiny .


Comando para arrancar el contenedor:

docker run -d --name flask --restart=always --mount type=volume,src=vol_destiny,dst=/webapp my_destiny


Debería arrancar en la dirección: http://172.17.0.2:8000

Si al hacer docker ps vemos que aparece pero que no podemos acceder a la url podemos ver donde debemos acceder utilizando:
docker inspect --format '{{ .NetworkSettings.IPAddress }}' <id_container>
