"""
Rule Extraction từ Random Forest - Trích xuất tri thức từ ML
Chuyển đổi Decision Trees thành quy tắc dễ hiểu cho KBS
"""

import pickle
import pandas as pd
from sklearn.tree import _tree
import logging
from config import MODEL_PATH, FEATURE_NAMES, NGANH_HOC_MAP, DATA_PATH

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RuleExtractor:
    """Trích xuất rules từ Decision Tree"""
    
    def __init__(self, model, feature_names):
        self.model = model
        self.feature_names = feature_names
        self.rules = []
    
    def extract_tree_rules(self, tree, feature_names):
        """Trích xuất rules từ một cây quyết định"""
        tree_ = tree.tree_
        feature_name = [
            feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
            for i in tree_.feature
        ]
        
        rules = []
        
        def recursive_extract(node, rules_path, depth=0):
            indent = "  " * depth
            
            if tree_.feature[node] != _tree.TREE_UNDEFINED:
                name = feature_name[node]
                threshold = tree_.threshold[node]
                
                # Đến nhánh trái (<=)
                left_path = rules_path + [(name, "<=", threshold)]
                recursive_extract(tree_.children_left[node], left_path, depth + 1)
                
                # Đến nhánh phải (>)
                right_path = rules_path + [(name, ">", threshold)]
                recursive_extract(tree_.children_right[node], right_path, depth + 1)
            else:
                # Leaf node - tạo rule
                samples = tree_.n_node_samples[node]
                value = tree_.value[node][0]
                predicted_class = value.argmax()
                confidence = value[predicted_class] / samples
                
                rules.append({
                    'conditions': rules_path,
                    'predicted_class': predicted_class,
                    'confidence': confidence,
                    'samples': samples
                })
        
        recursive_extract(0, [])
        return rules
    
    def extract_all_rules(self):
        """Trích xuất tất cả rules từ Random Forest"""
        logger.info("Trích xuất rules từ Random Forest...")
        
        all_rules = []
        for tree_idx, tree in enumerate(self.model.estimators_):
            tree_rules = self.extract_tree_rules(tree, self.feature_names)
            all_rules.extend(tree_rules)
            logger.info(f"  Tree {tree_idx+1}: {len(tree_rules)} rules")
        
        logger.info(f"Tổng cộng: {len(all_rules)} rules từ {len(self.model.estimators_)} cây")
        return all_rules
    
    def consolidate_rules(self, rules, top_k=50):
        """Gộp và sắp xếp rules theo độ tin cậy"""
        # Sắp xếp theo confidence & samples
        rules_sorted = sorted(
            rules, 
            key=lambda x: (x['confidence'], x['samples']), 
            reverse=True
        )
        
        # Lấy top rules
        top_rules = rules_sorted[:top_k]
        logger.info(f"Lấy {len(top_rules)} rules hàng đầu")
        
        return top_rules
    
    def format_rules_readable(self, rules):
        """Định dạng rules thành văn bản dễ đọc"""
        formatted = []
        for idx, rule in enumerate(rules, 1):
            major_name = NGANH_HOC_MAP[rule['predicted_class']]
            formatted.append(f"\nRule #{idx}")
            formatted.append("=" * 70)
            formatted.append(f"Dự đoán: {major_name}")
            formatted.append(f"Độ tin cậy: {rule['confidence']:.2%}")
            formatted.append(f"Số mẫu hỗ trợ: {rule['samples']}")
            formatted.append(f"\nĐiều kiện:")
            for feature, operator, threshold in rule['conditions']:
                formatted.append(f"  • {feature} {operator} {threshold:.2f}")
            formatted.append("")
        
        return "\n".join(formatted)


def analyze_feature_usage(rules, feature_names):
    """Phân tích tần suất sử dụng các feature trong rules"""
    feature_usage = {name: 0 for name in feature_names}
    
    for rule in rules:
        for feature, _, _ in rule['conditions']:
            if feature in feature_usage:
                feature_usage[feature] += 1
    
    # Sắp xếp theo tần suất
    sorted_usage = sorted(feature_usage.items(), key=lambda x: x[1], reverse=True)
    
    logger.info("\n📊 Tần suất sử dụng features trong rules:")
    for feature, count in sorted_usage:
        if count > 0:
            logger.info(f"  {feature:12s}: {count:4d} lần {'█' * (count // 5)}")
    
    return dict(sorted_usage)


def save_rules_to_file(rules, output_file='extracted_rules.txt'):
    """Lưu rules vào file"""
    extractor = RuleExtractor(None, FEATURE_NAMES)
    formatted = extractor.format_rules_readable(rules)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("EXTRACTED RULES FROM RANDOM FOREST\n")
        f.write("=" * 70 + "\n")
        f.write(f"Tổng số rules: {len(rules)}\n\n")
        f.write(formatted)
    
    logger.info(f"✓ Rules đã được lưu vào '{output_file}'")


def main():
    """Main function"""
    try:
        # 1. Load model
        logger.info("Load mô hình...")
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        logger.info("✓ Mô hình đã load")
        
        # 2. Extract rules
        extractor = RuleExtractor(model, FEATURE_NAMES)
        all_rules = extractor.extract_all_rules()
        
        # 3. Consolidate top rules
        logger.info("\n" + "=" * 70)
        top_rules = extractor.consolidate_rules(all_rules, top_k=50)
        
        # 4. Analyze feature usage
        logger.info("\n" + "=" * 70)
        feature_usage = analyze_feature_usage(top_rules, FEATURE_NAMES)
        
        # 5. Save rules
        logger.info("\n" + "=" * 70)
        save_rules_to_file(top_rules)
        
        # 6. Print sample rules
        logger.info("\n" + "=" * 70)
        logger.info("📋 Sample Top 5 Rules:")
        logger.info(extractor.format_rules_readable(top_rules[:5]))
        
        logger.info("\n" + "=" * 70)
        logger.info("✓ Rule extraction hoàn tất!")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ Lỗi: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()
