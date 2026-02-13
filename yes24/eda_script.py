
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import os

print("--- 데이터 분석 및 시각화 스크립트 시작 ---")

# 한글 폰트 설정
try:
    # Windows 환경
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    print("한글 폰트 'Malgun Gothic'을 설정했습니다.")
except Exception as e:
    print(f"폰트 설정 중 오류 발생 (무시하고 진행): {e}")
    # Mac 환경 예시
    # try:
    #     plt.rcParams['font.family'] = 'AppleGothic'
    #     plt.rcParams['axes.unicode_minus'] = False
    #     print("한글 폰트 'AppleGothic'을 설정했습니다.")
    # except Exception as e_mac:
    #      print(f"Mac 폰트 설정 중 오류 발생 (무시하고 진행): {e_mac}")


# 결과 저장 디렉토리 생성
output_dir = 'yes24/plots'
os.makedirs(output_dir, exist_ok=True)
print(f"'{output_dir}' 디렉토리에 결과가 저장됩니다.")

# --- 2. 데이터 불러오기 및 기본 정보 확인 ---
print("\n--- 2. 데이터 불러오기 및 기본 정보 확인 ---")
try:
    df = pd.read_csv('yes24/data/yes24_ai.csv')
    print("CSV 파일 불러오기 성공.")
except FileNotFoundError:
    print("에러: 'yes24/data/yes24_ai.csv' 파일을 찾을 수 없습니다.")
    exit()

print("데이터 일부 (head):")
print(df.head())
print("\n데이터 정보 (info):")
df.info()
print("\n수치 데이터 기술 통계 (describe):")
print(df.describe())

# --- 3. 데이터 정제 ---
print("\n--- 3. 데이터 정제 ---")
print("결측치 확인:")
print(df.isnull().sum())
print(f"\n중복 데이터 개수: {df.duplicated().sum()}")

# --- 4. 탐색적 데이터 분석 (EDA) 및 시각화 ---
print("\n--- 4. 탐색적 데이터 분석 (EDA) 및 시각화 ---")

# 4.1. 주요 수치 데이터 분포 확인
print("\n4.1. 주요 수치 데이터 분포 확인 및 저장...")
plt.figure(figsize=(10, 6))
sns.histplot(df['selling_price'], bins=30, kde=True)
plt.title('판매 가격 분포')
plt.xlabel('판매 가격')
plt.ylabel('도서 수')
plt.savefig(os.path.join(output_dir, 'selling_price_distribution.png'))
plt.close()
print("- 판매 가격 분포도 저장 완료.")

plt.figure(figsize=(10, 6))
sns.histplot(df['rating'].dropna(), bins=20, kde=True)
plt.title('평점 분포')
plt.xlabel('평점')
plt.ylabel('도서 수')
plt.savefig(os.path.join(output_dir, 'rating_distribution.png'))
plt.close()
print("- 평점 분포도 저장 완료.")

plt.figure(figsize=(10, 6))
sns.histplot(df['sales_index'], bins=30, kde=True)
plt.title('판매 지수 분포')
plt.xlabel('판매 지수')
plt.ylabel('도서 수')
plt.savefig(os.path.join(output_dir, 'sales_index_distribution.png'))
plt.close()
print("- 판매 지수 분포도 저장 완료.")

# 4.2. 상위 출판사 및 저자 분석
print("\n4.2. 상위 출판사 및 저자 분석 및 저장...")
plt.figure(figsize=(12, 8))
top_publishers = df['publisher'].value_counts().nlargest(10)
sns.barplot(x=top_publishers.values, y=top_publishers.index)
plt.title('상위 10개 출판사')
plt.xlabel('도서 수')
plt.ylabel('출판사')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'top_10_publishers.png'))
plt.close()
print("- 상위 10개 출판사 그래프 저장 완료.")

if not df['author'].dropna().empty:
    plt.figure(figsize=(12, 8))
    top_authors = df['author'].value_counts().nlargest(10)
    sns.barplot(x=top_authors.values, y=top_authors.index)
    plt.title('상위 10개 저자')
    plt.xlabel('도서 수')
    plt.ylabel('저자')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'top_10_authors.png'))
    plt.close()
    print("- 상위 10개 저자 그래프 저장 완료.")
else:
    print("- 저자 정보가 부족하여 그래프를 생성하지 않았습니다.")

# 4.3. 태그 키워드 분석 (워드클라우드)
print("\n4.3. 태그 키워드 분석 및 워드클라우드 저장...")
tags_data = df['tags'].dropna()
if not tags_data.empty:
    text = ' '.join(tags_data.str.replace('#', ' ').str.split(', ').explode().dropna())
    
    try:
        # 폰트 경로를 직접 지정
        font_path = 'c:/Windows/Fonts/malgun.ttf'
        if not os.path.exists(font_path):
             raise FileNotFoundError("Malgun Gothic font not found")

        wordcloud = WordCloud(
            font_path=font_path,
            width=800,
            height=400,
            background_color='white'
        ).generate(text)

        plt.figure(figsize=(15, 10))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('태그 키워드 워드클라우드')
        plt.savefig(os.path.join(output_dir, 'tags_wordcloud.png'))
        plt.close()
        print("- 태그 워드클라우드 저장 완료.")
    except Exception as e:
        print(f"- 워드클라우드 생성 중 에러 발생: {e}")
else:
    print("- 태그 정보가 부족하여 워드클라우드를 생성하지 않았습니다.")

# 4.4. 변수 간 상관관계 분석
print("\n4.4. 변수 간 상관관계 분석 및 히트맵 저장...")
numeric_cols = ['selling_price', 'rating', 'sales_index', 'review_count']
existing_cols = [col for col in numeric_cols if col in df.columns]

if len(existing_cols) > 1:
    corr_matrix = df[existing_cols].corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('주요 변수 간 상관관계')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'correlation_heatmap.png'))
    plt.close()
    print("- 상관관계 히트맵 저장 완료.")
else:
    print("- 상관관계 분석을 위한 수치형 데이터가 부족합니다.")

print("\n--- 모든 분석 및 시각화 완료 ---")
print(f"결과물은 '{output_dir}' 폴더에서 확인할 수 있습니다.")
