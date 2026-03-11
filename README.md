Setup Instructions

Docker comands:
docker-compose down  #stop the running containers
docker-compose build  #build the containers
docker-compose up  #start the containers
docker system prune -a  #delete all the images
docker ps  #show all the running containers
docker exec -it <container_id> bash  #execute the container image

Migrations commands:
alembic revision --autogenerate -m "initial migration"  #generate the migration file
alembic upgrade head  #apply the migration changes to database

Seed command:
python -m app.scripts.seed_db  #run the seed initialization script