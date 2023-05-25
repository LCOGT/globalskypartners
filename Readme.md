# LCO Global Sky Partners management app

Django app to for GSP to submit proposals, reports and manage users.


### Get snapshot of live site:

```
kubectl exec -it <pod-name> -n prod -c backend -- python manage.py dumpdata  -e sessions -e admin --natural-foreign --natural-primary | gzip > fullsite.json.gz
```

Read data into local sandbox with:
```
./manage.py migrate; ./manage.py loaddata fullsite.json.gz

## License

This project is licensed under the MIT License. Please see the
[LICENSE](LICENSE) file for details. 
