import cloudinary
import cloudinary.uploader


class UploadFileService:
    """
    Service for uploading files to Cloudinary.

    Provides functionality for configuring Cloudinary
    and uploading user avatar images.
    """

    def __init__(
        self,
        cloud_name,
        api_key,
        api_secret,
    ):
        """
        Initialize Cloudinary configuration.

        Args:
            cloud_name: Cloudinary cloud name.
            api_key: Cloudinary API key.
            api_secret: Cloudinary API secret.
        """

        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Upload image file to Cloudinary.

        Creates user avatar image with fixed size
        and returns generated image URL.

        Args:
            file: Uploaded image file.
            username: Username used for public image ID.

        Returns:
            URL of uploaded avatar image.
        """

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
