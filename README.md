Setup Instructions

Docker comands:
docker-compose down  #stop the docker
docker-compose build  #build the docker
docker-compose up  #run the docker
docker system prune -a  #delete the docker
docker ps  #go inside the container
docker exec -it <container_id> bash  #execute the container image

Migrations commands:
alembic revision --autogenerate -m "initial migration"  #generate the migration file
alembic upgrate head  #apply the migation

Seed command:
python -m app.scripts.seed_db  #initialize the database