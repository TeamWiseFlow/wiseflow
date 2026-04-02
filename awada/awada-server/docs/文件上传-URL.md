# 文件上传-URL

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/qw/doApi:
    post:
      summary: 文件上传-URL
      deprecated: false
      description: ''
      tags:
        - 云存储CDN模块
      parameters:
        - name: Content-Type
          in: header
          description: ''
          required: true
          example: application/json
          schema:
            type: string
        - name: X-QIWEI-TOKEN
          in: header
          description: ''
          example: '{{tokenId}}'
          schema:
            type: string
            default: '{{tokenId}}'
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                method:
                  type: string
                  title: /cloud/cdnBigUploadByUrl
                params:
                  type: object
                  properties:
                    guid:
                      type: string
                    filename:
                      type: string
                    fileUrl:
                      type: string
                    fileType:
                      type: integer
                      description: '1: jpg图片, 4: mp4视频, 5: 文件(也包括语音amr文件)'
                  required:
                    - guid
                    - filename
                    - fileUrl
                    - fileType
                  x-apifox-orders:
                    - guid
                    - filename
                    - fileUrl
                    - fileType
              required:
                - method
                - params
              x-apifox-orders:
                - method
                - params
            example:
              method: /cloud/cdnBigUploadByUrl
              params:
                guid: '{{guid}}'
                filename: ceshi.xls
                fileUrl: https://foo.com/xxx.xls
                fileType: 5
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                  data:
                    type: object
                    properties:
                      fileId:
                        type: string
                      fileKey:
                        type: string
                      fileMd5:
                        type: string
                      fileSize:
                        type: integer
                      fileThumbSize:
                        type: integer
                      cloudUrl:
                        type: string
                      fileAesKey:
                        type: string
                      filename:
                        type: string
                    required:
                      - fileAesKey
                      - fileId
                      - fileKey
                      - fileMd5
                      - fileSize
                      - fileThumbSize
                      - cloudUrl
                      - filename
                    x-apifox-orders:
                      - fileAesKey
                      - fileId
                      - fileKey
                      - fileMd5
                      - fileSize
                      - fileThumbSize
                      - filename
                      - cloudUrl
                  msg:
                    type: string
                required:
                  - code
                  - data
                  - msg
                x-apifox-orders:
                  - code
                  - data
                  - msg
              example:
                code: 0
                data:
                  fileAesKey: 32656637373664366**********64
                  fileId: >-
                    3069020102046230600201000204954ff05702030f424102043f7a5875020465e14218042466616365623137352d346531642d303332342**********31346662636231376202010002032c3ef004105c6ebc09c990d7ac3cae5f26b9390da50201010201000400
                  fileKey: faceb175-4e1d-0324-15bc-efc14fbcb17b
                  fileMd5: 5c6ebc09c990d7ac3cae5f26b9390da5
                  fileSize: 2899681
                  fileThumbSize: 7733
                  filename: stone.jpg
                  cloudUrl: >-
                    https://wochat-media-dev.oss-cn-beijing.aliyuncs.com/wochat/stone.jpg
                msg: 成功
          headers: {}
          x-apifox-name: 成功
      security: []
      x-apifox-folder: 云存储CDN模块
      x-apifox-status: released
      x-run-in-apifox: https://app.apifox.com/web/project/7051713/apis/api-344613900-run
components:
  schemas: {}
  securitySchemes: {}
servers: []
security: []

```