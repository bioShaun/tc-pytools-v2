import requests
import os

def download_assembly_report_by_filename(full_filename):
    """
    通过 NCBI 基因组文件名下载对应的 assembly_report.txt 文件。
    
    参数:
        full_filename (str): 完整的基因组文件名 (e.g., GCF_016699485.2_bGalGal1.mat.broiler.GRCg7b_genomic.fna.gz)
    
    返回:
        str: 成功下载的文件名或错误信息。
    """
    
    print(f"--- 正在解析文件名: {full_filename} ---")
    
    try:
        # 1. 解析文件名以获取前缀部分
        if "_genomic" in full_filename:
            prefix_end = full_filename.index("_genomic")
            full_prefix = full_filename[:prefix_end]
        else:
            raise ValueError("文件名格式不包含 '_genomic' 标识，无法自动解析 Assembly Name。")
        
        # 2. 提取 Assembly ID 和 Assembly Name
        parts = full_prefix.split('_', 2)
        if len(parts) < 3:
            raise ValueError("解析后的前缀部分不包含 Assembly ID 和 Name 后缀。")
        
        assembly_prefix = parts[0]  # GCF 或 GCA
        assembly_number = parts[1]  # 016699485.2
        assembly_name_suffix = parts[2]  # bGalGal1.mat.broiler.GRCg7b
        
        # 3. 构建 NCBI FTP 目录路径
        # NCBI 的目录结构: /genomes/all/GCF/016/699/485/GCF_016699485.2_xxx/
        # 需要将 assembly_number 拆分成三段
        number_parts = assembly_number.split('.')[0]  # 去掉版本号，获取 016699485
        
        # 将数字按每三位分组
        dir1 = number_parts[:3]   # 016
        dir2 = number_parts[3:6]  # 699
        dir3 = number_parts[6:9]  # 485
        
        # 4. 构造完整的 URL 路径
        base_url = "https://ftp.ncbi.nlm.nih.gov/genomes/all"
        report_file_name = f"{full_prefix}_assembly_report.txt"
        
        # 完整路径
        download_url = f"{base_url}/{assembly_prefix}/{dir1}/{dir2}/{dir3}/{full_prefix}/{report_file_name}"
        
        print(f"Assembly Prefix: {assembly_prefix}")
        print(f"Assembly Number: {assembly_number}")
        print(f"Assembly Name: {assembly_name_suffix}")
        print(f"目录路径: {assembly_prefix}/{dir1}/{dir2}/{dir3}/{full_prefix}/")
        print(f"尝试从以下 URL 下载文件:\n{download_url}")
        print("-" * 40)
        
        # 5. 发起 HTTP 请求并下载
        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()
        
        # 6. 保存文件
        local_filename = report_file_name
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return (f"✅ 文件 '{local_filename}' 成功下载。\n"
                f"   大小: {os.path.getsize(local_filename) / 1024:.2f} KB\n"
                f"   文件已保存到当前目录。")
        
    except ValueError as ve:
        return f"❌ 解析错误: {ve}"
    except requests.exceptions.HTTPError as errh:
        return (f"❌ HTTP 错误: 无法找到文件或路径不存在。\n"
                f"   状态码: {errh.response.status_code}\n"
                f"   URL: {errh.response.url}\n"
                f"   提示: 请检查文件名是否正确或该基因组是否存在于 NCBI FTP。")
    except requests.exceptions.RequestException as err:
        return f"❌ 发生网络/连接错误: {err}"

# --- 测试运行 ---
if __name__ == "__main__":
    test_filename = "GCF_016699485.2_bGalGal1.mat.broiler.GRCg7b_genomic.fna.gz"
    result = download_assembly_report_by_filename(test_filename)
    print("\n--- 结果 ---")
    print(result)