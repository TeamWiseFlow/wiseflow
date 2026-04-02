# 二维码-code验证

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
      summary: 二维码-code验证
      deprecated: false
      description: |-
        - 只有新实例登陆时才需要调用
        - 验证码验证成功后需再次调用[二维码-检测](api-344613857)即可登录成功
      tags:
        - 登陆模块
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
                  title: /login/verifyLoginQrcode
                params:
                  type: object
                  properties:
                    guid:
                      type: string
                    code:
                      type: string
                      title: 登录验证码
                  required:
                    - guid
                    - code
                  x-apifox-orders:
                    - guid
                    - code
                  x-apifox-ignore-properties: []
              required:
                - method
                - params
              x-apifox-orders:
                - method
                - params
              x-apifox-ignore-properties: []
            example:
              method: /login/verifyLoginQrcode
              params:
                guid: '{{guid}}'
                code: '464001'
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/%E5%93%8D%E5%BA%94%E6%88%90%E5%8A%9F'
          headers: {}
          x-apifox-name: 成功
      security: []
      x-apifox-folder: 登陆模块
      x-apifox-status: released
      x-run-in-apifox: https://app.apifox.com/web/project/7051713/apis/api-344613858-run
components:
  schemas:
    响应成功:
      type: object
      properties:
        data:
          type: object
          properties: {}
          x-apifox-orders: []
          x-apifox-ignore-properties: []
        code:
          type: integer
        msg:
          type: string
      required:
        - data
        - code
        - msg
      x-apifox-orders:
        - data
        - code
        - msg
      x-apifox-ignore-properties: []
      x-apifox-folder: ''
  securitySchemes: {}
servers: []
security: []

```