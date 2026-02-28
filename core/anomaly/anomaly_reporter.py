"""Format and report dosage anomalies."""

from typing import List, Dict
from dataclasses import asdict


class AnomalyReporter:
    """Generate user-friendly anomaly reports."""
    
    @staticmethod
    def format_report(anomaly_results: List[Dict]) -> Dict:
        """Format anomalies for UI display."""
        critical = []
        warnings = []
        infos = []
        
        for result in anomaly_results:
            if not result.get('has_anomaly'):
                continue
            
            formatted = {
                'medication': result.get('medication', 'Unknown'),
                'issue': result.get('primary_issue', ''),
                'severity': result.get('severity', 'unknown'),
                'recommendation': result.get('recommendation', ''),
                'details': result.get('additional_concerns', [])
            }
            
            severity = result.get('severity')
            if severity == 'danger':
                critical.append(formatted)
            elif severity == 'warning':
                warnings.append(formatted)
            else:
                infos.append(formatted)
        
        return {
            'has_issues': len(critical) > 0 or len(warnings) > 0,
            'critical_count': len(critical),
            'warning_count': len(warnings),
            'info_count': len(infos),
            'critical': critical,
            'warnings': warnings,
            'infos': infos,
            'summary': AnomalyReporter._generate_summary(critical, warnings)
        }
    
    @staticmethod
    def _generate_summary(critical: List, warnings: List) -> str:
        """Generate text summary."""
        if critical:
            return f"⚠️ {len(critical)} critical dosage issue(s) requiring immediate attention!"
        elif warnings:
            return f"⚡ {len(warnings)} dosage warning(s) - review recommended."
        return "✅ All dosages appear within safe ranges."
    
    @staticmethod
    def to_markdown(report: Dict) -> str:
        """Convert to markdown for display."""
        lines = ["## Dosage Validation Report", ""]
        
        if report['critical']:
            lines.append("### 🚨 Critical Issues")
            for item in report['critical']:
                lines.append(f"- **{item['medication']}**: {item['issue']}")
                lines.append(f"  - Recommendation: {item['recommendation']}")
            lines.append("")
        
        if report['warnings']:
            lines.append("### ⚠️ Warnings")
            for item in report['warnings']:
                lines.append(f"- **{item['medication']}**: {item['issue']}")
            lines.append("")
        
        lines.append(f"**Summary**: {report['summary']}")
        
        return "\n".join(lines)