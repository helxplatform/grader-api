import unittest
from unittest.mock import patch, MagicMock
from app.core.exceptions.token import DecodeTokenException
from app.services.jwt_service import JwtService

class TestJwtService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.jwt_service = JwtService()

    @patch('app.services.jwt_service.TokenHelper')
    async def test_verify_token_valid(self, mock_token_helper):
        mock_token_helper.decode.return_value = {"sub": "refresh", "id": 1, "onyen": "test_user"}
        await self.jwt_service.verify_token("valid_token")
        mock_token_helper.decode.assert_called_once_with(token="valid_token")

    @patch('app.services.jwt_service.TokenHelper')
    async def test_verify_token_invalid(self, mock_token_helper):
        mock_token_helper.decode.side_effect = DecodeTokenException()
        with self.assertRaises(DecodeTokenException):
            await self.jwt_service.verify_token("invalid_token")

    @patch('app.services.jwt_service.TokenHelper')
    async def test_refresh_access_token(self, mock_token_helper):
        mock_token_helper.decode.return_value = {"sub": "refresh", "id": 1, "onyen": "test_user"}
        mock_token_helper.encode.return_value = "new_access_token"

        result = await self.jwt_service.refresh_access_token("refresh_token")

        mock_token_helper.decode.assert_called_once_with(token="refresh_token")
        mock_token_helper.encode.assert_called_once_with(payload={"id": 1, "onyen": "test_user"}, expire_period=30)
        self.assertEqual(result, "new_access_token")

suite = unittest.TestLoader().loadTestsFromTestCase(TestJwtService)
unittest.TextTestRunner(verbosity=2).run(suite)
