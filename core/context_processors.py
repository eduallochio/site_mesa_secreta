from .models import ConfiguracaoSite


def site_config(request):
    """
    Context processor para disponibilizar as configurações do site
    em todos os templates automaticamente
    """
    return {
        'site_config': ConfiguracaoSite.get_config()
    }
