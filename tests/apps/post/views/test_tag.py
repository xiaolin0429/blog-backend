import pytest
from django.urls import reverse
from rest_framework import status
from apps.post.models import Tag

@pytest.mark.django_db
class TestTagViews:
    def test_list_tags_authenticated(self, auth_client):
        url = reverse('post:tag_list')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert isinstance(response.data['data']['results'], list)
        assert 'count' in response.data['data']

    def test_list_tags_unauthenticated(self, client):
        url = reverse('post:tag_list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 401
        assert "Authentication credentials were not provided" in response.data['message']

    def test_search_tags(self, auth_client, tag):
        url = reverse('post:tag_list')
        response = auth_client.get(f'{url}?search={tag.name}')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert isinstance(response.data['data']['results'], list)
        assert len(response.data['data']['results']) == 1
        assert response.data['data']['results'][0]['name'] == tag.name

    def test_create_tag(self, auth_client):
        url = reverse('post:tag_list')
        data = {
            'name': 'Test Tag',
            'description': 'Test Description'
        }
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['data']['name'] == data['name']
        assert response.data['data']['description'] == data['description']

    def test_create_tag_empty_name(self, auth_client):
        url = reverse('post:tag_list')
        data = {'name': ''}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 400
        assert response.data['message'] == "标签名称不能为空"

    def test_create_tag_invalid_length(self, auth_client):
        url = reverse('post:tag_list')
        data = {'name': 'a'}  # Too short
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 400
        assert response.data['message'] == "标签名称长度必须在2-50个字符之间"

        data = {'name': 'a' * 51}  # Too long
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 400
        assert response.data['message'] == "标签名称长度必须在2-50个字符之间"

    def test_create_tag_duplicate_name(self, auth_client, tag):
        url = reverse('post:tag_list')
        data = {'name': tag.name}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 409
        assert response.data['message'] == "标签名称已存在"

    def test_update_tag(self, auth_client, tag):
        url = reverse('post:tag_detail', kwargs={'pk': tag.id})
        data = {
            'name': 'Updated Tag',
            'description': 'Updated Description'
        }
        response = auth_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['data']['name'] == data['name']
        assert response.data['data']['description'] == data['description']

    def test_update_nonexistent_tag(self, auth_client):
        url = reverse('post:tag_detail', kwargs={'pk': 999})
        data = {
            'name': 'Updated Tag',
            'description': 'Updated Description'
        }
        response = auth_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 404
        assert response.data['message'] == "标签不存在"

    def test_delete_tag(self, auth_client, tag):
        url = reverse('post:tag_detail', kwargs={'pk': tag.id})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['message'] == "删除成功"

    def test_delete_nonexistent_tag(self, auth_client):
        url = reverse('post:tag_detail', kwargs={'pk': 999})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 404
        assert response.data['message'] == "标签不存在"

    def test_batch_create_tags(self, auth_client):
        url = reverse('post:tag_batch_create')
        data = [
            {'name': 'Tag 1', 'description': 'Description 1'},
            {'name': 'Tag 2', 'description': 'Description 2'},
            {'name': 'Tag 3', 'description': 'Description 3'}
        ]
        response = auth_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert len(response.data['data']) == 3
        for i, tag in enumerate(response.data['data']):
            assert tag['name'] == data[i]['name']
            assert tag['description'] == data[i]['description']

    def test_batch_create_tags_with_invalid_data(self, auth_client):
        url = reverse('post:tag_batch_create')
        data = [
            {'name': '', 'description': 'Description 1'},
            {'name': 'a', 'description': 'Description 2'},
            {'name': 'a' * 51, 'description': 'Description 3'}
        ]
        response = auth_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 400
        assert "标签名称" in response.data['message'] 