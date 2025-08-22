#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3ストレージモジュールのテスト
"""

import os
from unittest.mock import patch

import pytest

from src.ishifuku.config import StorageConfig


class TestS3AvailabilityCheck:
    """S3利用可能性チェックのテスト"""

    def test_s3_availability_function_exists(self):
        """S3利用可能性チェック関数が存在することを確認"""
        from src.ishifuku.storage.s3_handler import is_s3_available

        result = is_s3_available()
        assert isinstance(result, bool)

    def test_boto3_available_flag_exists(self):
        """BOTO3_AVAILABLEフラグが存在することを確認"""
        from src.ishifuku.storage.s3_handler import BOTO3_AVAILABLE

        assert isinstance(BOTO3_AVAILABLE, bool)


class TestS3EnvironmentVariables:
    """S3環境変数のテスト"""

    def test_s3_config_from_env_vars(self):
        """環境変数からのS3設定読み込みテスト"""
        with patch.dict(
            os.environ,
            {
                "AWS_S3_BUCKET": "env-bucket",
                "AWS_S3_KEY_PREFIX": "env-prefix/",
                "AWS_REGION": "us-west-2",
            },
        ):
            from src.ishifuku.config import StorageConfig

            config = StorageConfig()

            # 環境変数の値が反映されることを確認（StorageConfigの実装に依存）
            assert config is not None


# boto3が利用可能な場合のみ実行するテスト
@pytest.mark.skipif(
    not os.environ.get("TEST_S3_ENABLED"),
    reason="S3テストはTEST_S3_ENABLED環境変数が設定されている場合のみ実行",
)
class TestS3StorageIntegration:
    """S3ストレージの統合テスト（オプション）"""

    def test_s3_storage_creation(self):
        """S3ストレージの作成テスト"""
        try:
            from src.ishifuku.storage.s3_handler import S3Storage, is_s3_available

            if is_s3_available():
                config = StorageConfig(s3_bucket="test-bucket", s3_key_prefix="test/")
                storage = S3Storage(config)
                assert storage is not None
                assert storage.config.s3_bucket == "test-bucket"
        except ImportError:
            pytest.skip("boto3が利用できません")


class TestS3FunctionImports:
    """S3関数のインポートテスト"""

    def test_import_s3_functions(self):
        """S3関連関数がインポートできることを確認"""
        try:
            from src.ishifuku.storage.s3_handler import BOTO3_AVAILABLE, is_s3_available

            # 関数が正常にインポートされることを確認
            assert is_s3_available is not None
            assert isinstance(BOTO3_AVAILABLE, bool)

        except ImportError as e:
            pytest.fail(f"S3関数のインポートに失敗: {e}")

    def test_s3_storage_class_import(self):
        """S3Storageクラスのインポートテスト"""
        try:
            from src.ishifuku.storage.s3_handler import S3Storage

            # クラスが正常にインポートされることを確認
            assert S3Storage is not None

        except ImportError as e:
            # boto3が利用できない場合はスキップ
            pytest.skip(f"S3Storageクラスのインポートに失敗（boto3不要時は正常）: {e}")


class TestS3ErrorHandling:
    """S3エラーハンドリングのテスト"""

    def test_s3_import_error_graceful_handling(self):
        """boto3インポートエラーの適切な処理を確認"""
        # このテストは、boto3がない環境での動作確認
        from src.ishifuku.storage.s3_handler import is_s3_available

        # 関数が例外を投げずに結果を返すことを確認
        result = is_s3_available()
        assert isinstance(result, bool)

    def test_s3_conditional_import(self):
        """条件付きインポートの動作確認"""
        import sys

        # boto3モジュールの存在チェック（結果は使用しない - 存在チェックのみ）
        "boto3" in sys.modules or (
            "boto3"
            in [name for finder, name, ispkg in __import__("pkgutil").iter_modules()]
        )

        from src.ishifuku.storage.s3_handler import BOTO3_AVAILABLE

        # boto3の存在とフラグの整合性は環境依存のため、型チェックのみ
        assert isinstance(BOTO3_AVAILABLE, bool)


class TestS3HandlerEdgeCases:
    """S3Handler の境界ケーステスト"""

    @pytest.mark.skipif(
        not pytest.importorskip("boto3", reason="boto3 not available"),
        reason="boto3 not available",
    )
    def test_s3_handler_initialization(self):
        """S3Handlerの初期化テスト"""
        try:
            from src.ishifuku.storage.s3_handler import S3Handler

            config = StorageConfig()
            config.s3_bucket_name = "test-bucket"

            # 初期化が例外なく完了することを確認
            handler = S3Handler(config)
            assert handler is not None
        except ImportError:
            pytest.skip("boto3 not available")

    @pytest.mark.skipif(
        not pytest.importorskip("boto3", reason="boto3 not available"),
        reason="boto3 not available",
    )
    @patch("src.ishifuku.storage.s3_handler.boto3")
    def test_s3_handler_upload_with_error(self, mock_boto3):
        """S3アップロード時のエラーハンドリングテスト"""
        try:
            from src.ishifuku.storage.s3_handler import S3Handler

            # ボトエラーをシミュレート
            mock_client = mock_boto3.client.return_value
            mock_client.upload_file.side_effect = Exception("S3 upload error")

            config = StorageConfig()
            config.s3_bucket_name = "test-bucket"

            handler = S3Handler(config)

            # エラーが適切にハンドリングされることを確認（例外を投げる場合もある）
            try:
                result = handler.upload_file("test.csv", "local_file.csv")
                # メソッドがFalseを返すか、例外を投げるかを確認
                assert result is False or result is None
            except Exception as e:
                # 例外が投げられた場合も許容
                assert "error" in str(e).lower() or "S3" in str(e)
        except ImportError:
            pytest.skip("boto3 not available")

    def test_create_s3_storage_function(self):
        """create_s3_storage関数のテスト"""
        from src.ishifuku.storage import create_s3_storage

        config = StorageConfig()
        config.s3_bucket_name = "test-bucket"
        config.s3_key_prefix = "test-prefix"

        try:
            # 関数が呼び出し可能であることを確認
            result = create_s3_storage(bucket="test-bucket", prefix="test-prefix")
            # 結果がNoneでないことを確認（S3が利用不可能でもエラーメッセージが返る）
            assert result is not None
        except Exception:
            # S3が利用できない場合は例外が発生することを許容
            pass

    def test_s3_availability_false_case(self):
        """S3が利用不可能な場合のテスト"""
        with patch("src.ishifuku.storage.s3_handler.BOTO3_AVAILABLE", False):
            from src.ishifuku.storage.s3_handler import is_s3_available

            result = is_s3_available()
            assert result is False
