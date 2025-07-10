import os
import sys
import argparse
from pathlib import Path

# Цветное логирование
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log_info(message):
    print(f"{Colors.OKBLUE}[INFO]{Colors.ENDC} {message}")

def log_success(message):
    print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} {message}")

def log_warning(message):
    print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} {message}")

def log_error(message):
    print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} {message}")

def should_ignore(path, output_file):
    ignore_dirs = [
        '.git', '__pycache__', 'myenv','.vscode', '.idea', 
        'node_modules', 'venv', 'env', 'dist', 'build'
    ]
    ignore_exts = ['.pyc', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.pdf']
    
    # Игнорируем системные файлы и выходной файл
    if path.name == output_file or path.name.startswith('.'):
        return True
    
    # Игнорируем директории
    if any(part in ignore_dirs for part in path.parts):
        return True
    
    # Игнорируем файлы по расширению
    if path.suffix in ignore_exts:
        return True
    
    return False

def combine_files(root_dir, output_file):
    combined = []
    total_files = 0
    skipped_files = 0
    
    log_info(f"Starting project combination from: {root_dir}")
    
    for file_path in Path(root_dir).rglob('*'):
        if not file_path.is_file() or should_ignore(file_path, output_file):
            skipped_files += 1
            continue
        
        try:
            # Определяем относительный путь
            rel_path = file_path.relative_to(root_dir)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Добавляем разделитель с именем файла
            combined.append(f"\n\n{'=' * 50}\nFILE: {rel_path}\n{'=' * 50}\n\n")
            combined.append(content)
            total_files += 1
            
            log_info(f"Processed: {rel_path}")
        
        except UnicodeDecodeError:
            log_warning(f"Skipped binary file: {file_path}")
            skipped_files += 1
        except Exception as e:
            log_error(f"Error processing {file_path}: {str(e)}")
            skipped_files += 1
    
    # Сохраняем результат
    if combined:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(''.join(combined))
        log_success(f"Combined {total_files} files into {output_file}")
        log_success(f"Skipped {skipped_files} files/directories")
    else:
        log_error("No files were processed. Check directory structure and ignore rules.")

def main():
    parser = argparse.ArgumentParser(description='Combine project files into single text file')
    parser.add_argument('-d', '--directory', default='.', help='Project directory (default: current)')
    parser.add_argument('-o', '--output', default='combined_project.txt', help='Output file (default: combined_project.txt)')
    args = parser.parse_args()
    
    project_dir = Path(args.directory).resolve()
    output_file = args.output
    
    if not project_dir.exists() or not project_dir.is_dir():
        log_error(f"Directory not found: {project_dir}")
        sys.exit(1)
    
    log_info(f"Project directory: {project_dir}")
    log_info(f"Output file: {output_file}")
    
    combine_files(project_dir, output_file)

if __name__ == "__main__":
    main()