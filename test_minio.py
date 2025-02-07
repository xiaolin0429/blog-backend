from minio import Minio

client = Minio(
    "localhost:9000", access_key="minioadmin", secret_key="minioadmin", secure=False
)
print("Buckets:", [bucket.name for bucket in client.list_buckets()])
