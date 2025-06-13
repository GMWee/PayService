docker build -t gmwee_payment .
docker tag gmwee_payment:latest registry.teefusion.net/tier-i/gmwee_payment:dev
docker push registry.teefusion.net/tier-i/gmwee_payment:dev
