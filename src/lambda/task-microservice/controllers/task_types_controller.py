from aws_lambda_powertools.event_handler.router import APIGatewayRouter

router = APIGatewayRouter()


@router.get('/')
def list_task_types():
    return {
        "Count": 3,
        "Items": [
            {
                "InputTemplate": {
                    "$id": "https://infradinamica.org/schemas/pavimenta2.image_bundle.json",
                    "type": "object",
                    "properties": {
                        "Geography": {
                            "type": "string",
                            "description": "Geographical reference like roadway name."
                        },
                        "GeographySource": {
                            "type": "string",
                            "description": "Dataset slug from which geographical reference was taken."
                        },
                        "ImageBundle": {
                            "type": "object",
                            "description": "Array of zip files attached with images to analize.",
                            "s3Multiple": True,
                            "properties": {
                                "Extension": {
                                    "const": "zip",
                                    "default": "zip"
                                },
                                "Content": {
                                    "$ref": "infradigital.defs.json#/definitions/S3ObjectArray"
                                }
                            }
                        },
                        "Type": {
                            "description": "Define the attached payload.",
                            "const": "image_bundle",
                            "default": "image_bundle"
                        }
                    },
                    "required": [
                        "Geography",
                        "GeographySource",
                        "ImageBundle",
                        "Type"
                    ],
                    "additionalProperties": False
                },
                "Id": 1,
                "Name": "Pavimentos Road Sections - Image Bundle",
                "Description": "Pavimentados road sections analisis in an array of compressed in zip files with image files within, each image must have embedded GPS metadata",
                "FnName": "arn:aws:states:us-east-1:195419001736:stateMachine:pavimenta2-road-section-workflow-dev",
                "AppId": 2,
                "Resource": "aws-sagemaker",
                "AppServiceSlug": "pavimenta2#road_sections_inference",
                "Path": "road_sections_inference",
                "ExecOnSubmit": False,
                "AppName": "Pavimentados"
            },
            {
                "InputTemplate": {
                    "$id": "https://infradinamica.org/schemas/pavimenta2.image_bundle_gps.json",
                    "type": "object",
                    "properties": {
                        "Geography": {
                            "type": "string",
                            "description": "Geographical reference like roadway name."
                        },
                        "GeographySource": {
                            "type": "string",
                            "description": "Dataset slug from which geographical reference was taken."
                        },
                        "ImageBundle": {
                            "type": "object",
                            "description": "Array of zip files attached with images to analize.",
                            "s3Multiple": True,
                            "properties": {
                                "Extension": {
                                    "const": "zip",
                                    "default": "zip"
                                },
                                "Content": {
                                    "$ref": "infradigital.defs.json#/definitions/S3ObjectArray"
                                }
                            }
                        },
                        "GpsFile": {
                            "type": "object",
                            "description": "File attached with GPS data in GPRRA format.",
                            "s3Multiple": False,
                            "properties": {
                                "Extension": {
                                    "type": "string",
                                    "pattern": "(log|txt)$",
                                    "default": "log"
                                },
                                "Content": {
                                    "$ref": "infradigital.defs.json#/definitions/S3Object"
                                }
                            }
                        },
                        "Type": {
                            "description": "Define the attached payload.",
                            "const": "image_bundle_gps",
                            "default": "image_bundle_gps"
                        }
                    },
                    "required": [
                        "Geography",
                        "GeographySource",
                        "ImageBundle",
                        "GpsFile",
                        "Type"
                    ],
                    "additionalProperties": False
                },
                "Id": 2,
                "Name": "Pavimentos Road Sections - Image Bundle GPS",
                "Description": "Pavimentados road sections analisis in an array of compressed in zip files with image files within and a log file with GPS records of the route",
                "FnName": "arn:aws:states:us-east-1:195419001736:stateMachine:pavimenta2-road-section-workflow-dev",
                "AppId": 2,
                "Resource": "aws-sagemaker",
                "AppServiceSlug": "pavimenta2#road_sections_inference",
                "Path": "road_sections_inference",
                "ExecOnSubmit": False,
                "AppName": "Pavimentados"
            },
            {
                "InputTemplate": {
                    "$id": "https://infradinamica.org/schemas/pavimenta2.video_gps.json",
                    "type": "object",
                    "properties": {
                        "Geography": {
                            "type": "string",
                            "description": "Geographical reference like roadway name."
                        },
                        "GeographySource": {
                            "type": "string",
                            "description": "Dataset slug from which geographical reference was taken."
                        },
                        "VideoFile": {
                            "type": "object",
                            "description": "Video file to analize.",
                            "s3Multiple": False,
                            "properties": {
                                "Extension": {
                                    "const": "mp4",
                                    "default": "mp4"
                                },
                                "Content": {
                                    "$ref": "infradigital.defs.json#/definitions/S3Object"
                                }
                            }
                        },
                        "GpsFile": {
                            "type": "object",
                            "description": "File attached with GPS data in GPRRA format.",
                            "s3Multiple": False,
                            "properties": {
                                "Extension": {
                                    "type": "string",
                                    "pattern": "(log|txt)$",
                                    "default": "log"
                                },
                                "Content": {
                                    "$ref": "infradigital.defs.json#/definitions/S3Object"
                                }
                            }
                        },
                        "Type": {
                            "description": "Define the attached payload.",
                            "const": "video_gps",
                            "default": "video_gps"
                        }
                    },
                    "required": [
                        "Geography",
                        "GeographySource",
                        "VideoFile",
                        "GpsFile",
                        "Type"
                    ],
                    "additionalProperties": False
                },
                "Id": 3,
                "Name": "Pavimentos Road Sections - Video GPS",
                "Description": "Pavimentados road sections analisis in an MP4 file and a log file with GPS records of the route",
                "FnName": "arn:aws:states:us-east-1:195419001736:stateMachine:pavimenta2-road-section-workflow-dev",
                "AppId": 2,
                "Resource": "aws-sagemaker",
                "AppServiceSlug": "pavimenta2#road_sections_inference",
                "Path": "road_sections_inference",
                "ExecOnSubmit": False,
                "AppName": "Pavimentados"
            }
        ]
    }