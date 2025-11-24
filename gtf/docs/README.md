# Rename NGDC Genome ID

重命名 NGDC 基因组 FASTA 和 GFF 文件中的染色体 ID，使用 OriSeqID 替换 GWHGECT 格式的 ID。

## 功能说明

从 FASTA 文件头中提取 OriSeqID，并将其替换为 GWHGECT 格式的 ID。

### FASTA 头示例

```
>GWHGECT00000001.1      Chromosome 1A   Complete=T      Circular=F      OriSeqID=Chr1A  Len=600907804
```

将被转换为：

```
>Chr1A
```

## 使用方法

### 基本用法

```bash
# 只处理 FASTA 文件
uv run rename-ngdc-genome-id -f genome.fasta -o output.fasta

# 同时处理 FASTA 和 GFF 文件
uv run rename-ngdc-genome-id -f genome.fasta -o output.fasta -g input.gff -og output.gff
```

### 命令行参数

```
usage: rename-ngdc-genome-id [-h] -f FASTA -o OUTPUT [-g GFF] [-og OUTPUT_GFF]

Rename chromosome IDs in NGDC genome FASTA and GFF files using OriSeqID

options:
  -h, --help            show this help message and exit
  -f FASTA, --fasta FASTA
                        Input FASTA file
  -o OUTPUT, --output OUTPUT
                        Output FASTA file
  -g GFF, --gff GFF     Input GFF file (optional)
  -og OUTPUT_GFF, --output-gff OUTPUT_GFF
                        Output GFF file (optional, required if -g is specified)
```

## 使用示例

### 示例 1: 只处理 FASTA 文件

```bash
uv run rename-ngdc-genome-id \
    -f GWHGECT00000000.genome.fasta \
    -o genome_renamed.fasta
```

### 示例 2: 同时处理 FASTA 和 GFF

```bash
uv run rename-ngdc-genome-id \
    -f GWHGECT00000000.genome.fasta \
    -o genome_renamed.fasta \
    -g GWHGECT00000000.gff \
    -og genome_renamed.gff
```

### 示例 3: 直接使用（已安装情况下）

```bash
# 如果已经安装到系统
rename-ngdc-genome-id -f input.fasta -o output.fasta
```

## 输入文件格式

### FASTA 格式

标准 FASTA 格式，头部必须包含 `OriSeqID=` 字段：

```
>GWHGECT00000001.1      Chromosome 1A   Complete=T      Circular=F      OriSeqID=Chr1A  Len=600907804
ATCGATCGATCGATCG...
>GWHGECT00000002.1      Chromosome 1B   Complete=T      Circular=F      OriSeqID=Chr1B  Len=731628012
GCTAGCTAGCTAGCTA...
```

### GFF 格式

标准 GFF3 格式，第一列为染色体 ID：

```
##gff-version 3
GWHGECT00000001.1	RefSeq	gene	100	200	.	+	.	ID=gene1;Name=GENE1
GWHGECT00000001.1	RefSeq	mRNA	100	200	.	+	.	ID=transcript1;Parent=gene1
```

## 输出文件格式

### 输出 FASTA

简化的 FASTA 头，只保留新的染色体 ID：

```
>Chr1A
ATCGATCGATCGATCG...
>Chr1B
GCTAGCTAGCTAGCTA...
```

### 输出 GFF

染色体 ID 已替换，其他字段保持不变：

```
##gff-version 3
Chr1A	RefSeq	gene	100	200	.	+	.	ID=gene1;Name=GENE1
Chr1A	RefSeq	mRNA	100	200	.	+	.	ID=transcript1;Parent=gene1
```

## 注意事项

1. **必需的 OriSeqID**: FASTA 文件头中必须包含 `OriSeqID=` 字段，否则该序列将保持原样
2. **GFF 依赖 FASTA**: GFF 文件的处理依赖于从 FASTA 文件中提取的 ID 映射
3. **文件编码**: 默认使用 UTF-8 编码
4. **内存使用**: ID 映射表会全部加载到内存，但序列数据是流式处理

## 错误处理

如果 FASTA 头中没有找到 `OriSeqID`，该序列的头部将保持原样，程序会继续处理其他序列。

程序会在标准错误输出中显示处理进度和 ID 映射信息：

```
Building ID mapping from input.fasta...
Found 21 chromosome mappings
  GWHGECT00000001.1 -> Chr1A
  GWHGECT00000002.1 -> Chr1B
  ...
Renaming FASTA file to output.fasta...
Renaming GFF file to output.gff...
Done!
```

## Python API 使用

如果需要在 Python 代码中使用：

```python
from gtf.rename_ngdc_genome_id import build_id_mapping, rename_fasta, rename_gff

# 构建 ID 映射
id_map = build_id_mapping('input.fasta')

# 重命名 FASTA
rename_fasta('input.fasta', 'output.fasta', id_map)

# 重命名 GFF
rename_gff('input.gff', 'output.gff', id_map)
```

## 性能说明

- 处理速度主要取决于文件 I/O
- ID 映射构建：O(n)，n 为序列数量
- FASTA 重命名：O(n)，n 为文件行数
- GFF 重命名：O(m)，m 为 GFF 行数
- 内存占用：ID 映射表 + 当前处理行的大小

对于大型基因组文件，处理速度通常在几秒到几分钟之间。
