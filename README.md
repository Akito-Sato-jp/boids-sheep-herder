# Boids-based Sheep Herder
Pythonとtkinterで制作した、ボイド（群れ）アルゴリズムを用いた羊追いアクションゲームです。

## 🎥 動作デモ
![羊追いゲームのデモ](./Sheep.gif)
※犬（プレイヤー）を操作して、羊の群れを誘導します。

## 🧠 技術的な見どころ：ボイド（Boids）アルゴリズム
このプロジェクトでは、以下の3つのベクトル演算を組み合わせることで、羊たちのリアルな群れの動きを実現しています。

1. **分離（Separation）**: 羊同士の衝突を避ける動き
2. **整列（Alignment）**: 周囲の群れと同じ方向に進む動き
3. **結合（Cohesion）**: 群れの中央に集まろうとする動き

これに「プレイヤーから一定距離で逃げる」ロジックを追加し、生き生きとした回避行動をプログラミングしました。

## 🛠 使用技術
- **Language:** Python 3.11
- **Library:** tkinter, Pillow (PIL)
- **Mathematical Logic:** ベクトル演算によるアルゴリズム実装

## 📂 ファイル構成
- `sheep.py`: ゲームのメインコード
- `Sheep.gif`: 動作デモ画像
- `dog.png` / `sheep.png` / `grass.jpg`: ゲーム内アセット

## 🎮 実行方法
1. Pythonがインストールされた環境で本リポジトリをクローンします。
2. 以下のコマンドでライブラリをインストールします（必要な場合）。
   `pip install Pillow`
3. プログラムを実行します。
   `python sheep.py`

🤖 AI-Assisted Development
This project was developed with the assistance of AI (Google Gemini / GitHub Copilot).
I used AI for brainstorming algorithms, debugging complex errors, and optimizing code structure, while maintaining full control over the final architecture and logic.

（このプロジェクトはAIの支援を受けて開発しました。アルゴリズムの検討、デバッグ、コードの最適化にAIを活用し、最終的な設計やロジックの検証はすべて自身で行っています。）
