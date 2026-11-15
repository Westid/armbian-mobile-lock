ДЛя теста делать запуск контейнера в таком формате
docker run -itd --name bondar-project \
  --mount source=/home/stepan/project,target=/app,type=bind \
  --mount type=bind,source="$(readlink -f /tmp/ttyV0)",target=/dev/ttyV0 \
  -p 8080:8080 start_dev /bin/bash

В проде mount /tmp/ttyV0 скорее всего будет выполнен через --device, потому как сейчас временно создан порт, для имитации работы оного в RaspberryPi.
Пока следует протестировать код, затем оформить