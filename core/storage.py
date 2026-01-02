"""
Custom Storage Backend para Supabase Storage
"""
import os
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings
from supabase import create_client, Client
from urllib.parse import urljoin


class SupabaseStorage(Storage):
    """
    Storage backend personalizado para Supabase Storage
    """
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY
        self.bucket_name = settings.SUPABASE_BUCKET_NAME
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
    def _get_storage_client(self):
        """Retorna o cliente de storage do Supabase"""
        return self.supabase.storage.from_(self.bucket_name)
    
    def _save(self, name, content):
        """
        Salva o arquivo no Supabase Storage
        """
        # Garantir que o nome do arquivo seja único
        name = self.get_available_name(name)
        
        # Ler o conteúdo do arquivo
        if hasattr(content, 'read'):
            file_content = content.read()
        else:
            file_content = content
        
        # Upload para o Supabase
        storage_client = self._get_storage_client()
        
        try:
            # Upload do arquivo
            response = storage_client.upload(
                path=name,
                file=file_content,
                file_options={"content-type": self._guess_content_type(name)}
            )
            return name
        except Exception as e:
            raise IOError(f"Erro ao fazer upload para Supabase Storage: {str(e)}")
    
    def _open(self, name, mode='rb'):
        """
        Abre um arquivo do Supabase Storage
        """
        storage_client = self._get_storage_client()
        
        try:
            file_content = storage_client.download(name)
            return ContentFile(file_content)
        except Exception as e:
            raise IOError(f"Erro ao baixar arquivo do Supabase Storage: {str(e)}")
    
    def delete(self, name):
        """
        Deleta um arquivo do Supabase Storage
        """
        storage_client = self._get_storage_client()
        
        try:
            storage_client.remove([name])
        except Exception as e:
            # Não levanta erro se arquivo não existir
            pass
    
    def exists(self, name):
        """
        Verifica se o arquivo existe no Supabase Storage
        """
        storage_client = self._get_storage_client()
        
        try:
            # Lista arquivos no bucket
            files = storage_client.list()
            return any(file['name'] == name for file in files)
        except Exception:
            return False
    
    def url(self, name):
        """
        Retorna a URL pública do arquivo
        """
        storage_client = self._get_storage_client()
        
        try:
            # Gera URL pública
            public_url = storage_client.get_public_url(name)
            return public_url
        except Exception as e:
            # URL padrão caso ocorra erro
            return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{name}"
    
    def size(self, name):
        """
        Retorna o tamanho do arquivo em bytes
        """
        storage_client = self._get_storage_client()
        
        try:
            files = storage_client.list()
            for file in files:
                if file['name'] == name:
                    return file.get('metadata', {}).get('size', 0)
            return 0
        except Exception:
            return 0
    
    def get_available_name(self, name, max_length=None):
        """
        Retorna um nome de arquivo disponível
        """
        import uuid
        from pathlib import Path
        
        # Pegar extensão do arquivo
        ext = Path(name).suffix
        # Gerar nome único
        unique_name = f"{uuid.uuid4().hex}{ext}"
        
        return unique_name
    
    def _guess_content_type(self, name):
        """
        Adivinha o content-type baseado na extensão do arquivo
        """
        import mimetypes
        content_type, _ = mimetypes.guess_type(name)
        return content_type or 'application/octet-stream'
