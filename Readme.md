# LCO Global Sky Partners management app

Django app to for GSP to submit proposals, reports and manage users.

## Configuration

Environment variables needed for production:

| Name         | Description                             | Default Value |
|:-------------|:----------------------------------------|:--------------|
| `SECRET_KEY` | Django Secret Key (required)            | N/A           |
| `DEBUG`      | Enable Django Debug mode                | `False`       |
| `DB_HOST`    | PostgreSQL Database Hostname (required) | N/A           |
| `DB_NAME`    | PostgreSQL Database Name (required)     | N/A           |
| `DB_USER`    | PostgreSQL Database Username (required) | N/A           |
| `DB_PASS`    | PostgreSQL Database Password (required) | N/A           |

## Build

This project is built automatically by the [LCO Jenkins Server](http://jenkins.lco.gtn/).
Please see the [Jenkinsfile](Jenkinsfile) for details.

## Production Deployment

This project is deployed on the LCO Kubernetes Cluster. Please see the
[LCO Helm Charts Repository](https://github.com/LCOGT/helm-charts) for details.

## License

This project is licensed under the MIT License. Please see the
[LICENSE](LICENSE) file for details.
