#!/bin/bash

# AWS SAMを使用したデプロイメントスクリプト
# 使用方法: ./sam_deploy.sh [環境名] [S3バケット名]

set -e

# 引数の設定
ENVIRONMENT=${1:-dev}
S3_BUCKET_NAME=${2:-ishifuku-gold-data}
STACK_NAME="ishifuku-scraper-${ENVIRONMENT}"
REGION="ap-northeast-1"

echo "===================="
echo "AWS SAM デプロイメント"
echo "===================="
echo "Environment: ${ENVIRONMENT}"
echo "Stack Name: ${STACK_NAME}"
echo "S3 Bucket: ${S3_BUCKET_NAME}-${ENVIRONMENT}"
echo "Region: ${REGION}"
echo "===================="

# 必要なツールの確認
command -v sam >/dev/null 2>&1 || { echo "AWS SAM CLIがインストールされていません"; exit 1; }
command -v aws >/dev/null 2>&1 || { echo "AWS CLIがインストールされていません"; exit 1; }

# AWS認証の確認
aws sts get-caller-identity >/dev/null 2>&1 || { echo "AWS認証が設定されていません"; exit 1; }

# SAMアプリケーションのビルド
echo "SAMアプリケーションをビルド中..."
sam build --template-file template.yaml

# デプロイメント用S3バケット（SAM用）の作成確認
SAM_BUCKET="sam-deployments-${REGION}-$(aws sts get-caller-identity --query Account --output text)"
aws s3 ls "s3://${SAM_BUCKET}" >/dev/null 2>&1 || {
    echo "SAMデプロイメント用バケットを作成中: ${SAM_BUCKET}"
    aws s3 mb "s3://${SAM_BUCKET}" --region ${REGION}
}

# デプロイメント実行
echo "Lambda関数をデプロイ中..."
sam deploy \
    --template-file .aws-sam/build/template.yaml \
    --stack-name ${STACK_NAME} \
    --s3-bucket ${SAM_BUCKET} \
    --parameter-overrides \
        Environment=${ENVIRONMENT} \
        S3BucketName=${S3_BUCKET_NAME} \
    --capabilities CAPABILITY_IAM \
    --region ${REGION} \
    --confirm-changeset

# デプロイメント結果の表示
echo "===================="
echo "デプロイメント完了！"
echo "===================="

# スタック情報の取得
FUNCTION_ARN=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --query 'Stacks[0].Outputs[?OutputKey==`GoldScrapingFunctionArn`].OutputValue' \
    --output text \
    --region ${REGION})

API_URL=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text \
    --region ${REGION})

BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
    --output text \
    --region ${REGION})

echo "Lambda関数ARN: ${FUNCTION_ARN}"
echo "API URL: ${API_URL}"
echo "S3バケット: ${BUCKET_NAME}"
echo ""
echo "テスト実行方法:"
echo "  手動実行: curl ${API_URL}"
echo "  直接実行: aws lambda invoke --function-name ${FUNCTION_ARN} --region ${REGION} response.json"
echo ""
echo "ログ確認方法:"
echo "  aws logs tail '/aws/lambda/ishifuku-scraper-${ENVIRONMENT}' --follow --region ${REGION}"
echo ""
echo "S3ファイル確認方法:"
echo "  aws s3 ls s3://${BUCKET_NAME}/ --recursive"
