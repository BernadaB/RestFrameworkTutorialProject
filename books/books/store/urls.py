from rest_framework.routers import SimpleRouter

from .views import BookViewSet

router = SimpleRouter()
router.register(r'book', BookViewSet)
urlpatterns = []
urlpatterns += router.urls
