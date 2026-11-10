from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

_LUU_TOKEN = """
    responseInterceptor: (response) => {
      try {
        const url = String(response.url || "")
        const thanhCong = response.ok && response.status >= 200 && response.status < 300
        if (!thanhCong || !/\\/auth\\/(login|register)(?:\\?|$)/.test(url)) return response
        let data = response.data != null ? response.data : response.body
        if (typeof data === "string") {
          try { data = JSON.parse(data) } catch (error) { data = null }
        }
        const token = data && data.access_token
        if (token && window.ui) {
          window.ui.authActions.authorize({
            BearerAuth: {
              name: "BearerAuth",
              schema: { type: "http", scheme: "bearer", bearerFormat: "JWT" },
              value: token,
            },
          })
          if (window.ui.authActions.persistAuthorizationIfNeeded) {
            window.ui.authActions.persistAuthorizationIfNeeded()
          }
        }
      } catch (error) { /* Giữ nguyên phản hồi nếu không lưu được token. */ }
      return response
    },
"""


def docs_html(*, openapi_url: str, title: str) -> HTMLResponse:
    """Swagger UI có sẵn nút Authorize và tự lưu token sau khi đăng nhập hoặc đăng ký."""
    page = get_swagger_ui_html(
        openapi_url=openapi_url,
        title=title,
        swagger_ui_parameters={"persistAuthorization": True},
    )
    html = page.body.decode()
    html = html.replace("const ui = SwaggerUIBundle({", "const ui = window.ui = SwaggerUIBundle({", 1)
    html = html.replace("presets: [", _LUU_TOKEN + "    presets: [", 1)
    return HTMLResponse(html)
