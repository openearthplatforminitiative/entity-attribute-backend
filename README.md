# Entity Attribute Backend
![Build Status](https://github.com/openearthplatforminitiative/entity-attribute-backend/actions/workflows/master-release.yml/badge.svg)
![License](https://img.shields.io/github/license/openearthplatforminitiative/entity-attribute-backend)
![Last Commit](https://img.shields.io/github/last-commit/openearthplatforminitiative/entity-attribute-backend)
![GitHub issues](https://img.shields.io/github/issues/openearthplatforminitiative/entity-attribute-backend)
![GitHub pull requests](https://img.shields.io/github/issues-pr/openearthplatforminitiative/entity-attribute-backend)

A dynamic backend for registry applications.

This backend provides a simple interface to manage entities and their attributes, allowing for easy storage, retrieval, and manipulation of data.
This might be useful for applications that require a flexible and extensible way to handle various types of data entities.
It is designed to be a quick way to get started with entity management without the need for complex database schemas or configurations.

## Features
- **Entity Management**: Create, read, update, and delete entities.
- **Attribute Management**: Add, update, and remove attributes for entities.
- **Flexible Schema**: Entities can have any number of attributes with different data types.
- **Simple Interface**: Easy-to-use API for managing entities and attributes.

## Supported data types
- String
- Integer
- Float
- Boolean
- Date
- Enum (with predefined values)
- Geometry (Point, LineString, Polygon)

The backend is also capable of handling assets (files, images, etc.) associated with entities, allowing for a more comprehensive data management solution.

## Installation
The entity attribute backend depends on a PostgreSQL database.
There are several options for installing and running the Entity Attribute Backend:
* **Using docker compose**: This is the recommended way to run the backend, as it simplifies the setup process and ensures that all dependencies are correctly configured.
* **Using poetry**: Use this method if you plan to develop the backend further. You will need to install the dependencies and set up the database manually.

### Running with Docker Compose
This is the simplest way to run the Entity Attribute Backend, as it automatically sets up all necessary dependencies and configurations.
To run the Entity Attribute Backend using Docker, follow these steps:
1. **Clone the repository**:
   ```bash
   git clone git@github.com:openearthplatforminitiative/entity-attribute-backend.git
    ```
2. **Navigate to the project directory**:
   ```bash
   cd entity-attribute-backend
   ```
3. **Start the backend**:
   ```bash
    docker-compose up
    ```
   
### Running with poetry
To run the Entity Attribute Backend using Docker, follow these steps:
1. Setup a PostgreSQL database. You can use a local PostgreSQL instance or a cloud-based service like AWS RDS or Google Cloud SQL.
   - Create a database named `entity_attribute_backend`.
   - Create a user with the necessary permissions to access the database.
 
2. **Clone the repository**:
   ```bash
   git clone git@github.com:openearthplatforminitiative/entity-attribute-backend.git
    ```
3. **Navigate to the project directory**:
    ```bash
   cd entity-attribute-backend
   ```
4. **Install dependencies**:
   ```bash
   poetry install
   ```
5. **Set environment variables**:
    Create a `.env` file in the root directory of the project with the following content:
    ```env
    POSTGRES_USER=<username>
    POSTGRES_PASSWORD=<password>
    POSTGRES_DB=entity_attribute_backend
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    POSTGRES_SCHEMA=public
    ```
    Replace `<username>` and `<password>` with your PostgreSQL credentials.

## Configuring the Backend
See the article on [Configuring the Entity Attribute Backend](https://developer.openepi.io/how-tos/generic-backend)

## Contributing
Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for details on how to contribute to this project.

## License
This project is licensed under the Apache-2.0 License  - see the [LICENSE](LICENSE) file for details.

## Contact
For any questions or issues, please open an issue on the [GitHub repository](https://github.com/openearthplatforminitiative/entity-attribute-backend)