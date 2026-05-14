import cloudinary
import cloudinary.uploader


class UploadFileService:
    def __init__(
        self,
        cloud_name,
        api_key,
        api_secret,
    ):
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        public_id = f"ContactsApp/{username}"

        r = cloudinary.uploader.upload(
            file.file,
            public_id=public_id,
            overwrite=True,
        )

        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250,
            height=250,
            crop="fill",
            version=r.get("version"),
        )

        return src_url
