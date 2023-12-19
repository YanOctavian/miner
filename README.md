## 创建虚拟环境
```angular2html
python3 -m venv venv
source venv/bin/activate

```
## 安装依赖
```
pip install -r requirements.txt
```

## 在miner.py中的ss列表里填写你的私钥
```
if __name__ == "__main__":

    ss = [
        # 填写你的私钥
        "0x你的私钥",
    ]
```

## 启动程序
```angular2html
python miner.py
```