# =============================================================================
# LOGISTICS CASCADE FAILURE PREDICTOR
# A Graph-Based Disruption Simulation and ML Risk Prediction System
# =============================================================================

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("LOGISTICS CASCADE FAILURE PREDICTOR")
print("A Graph-Based Supply Chain Disruption Simulator")
print("=" * 80)

# =============================================================================
# PHASE 1: DATA GENERATION
# =============================================================================
print("\n[PHASE 1] GENERATING SYNTHETIC LOGISTICS DATA...")

# Create Nodes Dataset
nodes_data = {
    'node_id': list(range(1, 18)),
    'node_type': ['Supplier']*3 + ['Warehouse']*3 + ['Factory']*2 + ['Distribution_Center']*3 + ['Customer']*6,
    'node_name': ['Supplier_A', 'Supplier_B', 'Supplier_C',
                  'Warehouse_X', 'Warehouse_Y', 'Warehouse_Z',
                  'Factory_1', 'Factory_2',
                  'DC_North', 'DC_South', 'DC_East',
                  'Customer_1', 'Customer_2', 'Customer_3', 'Customer_4', 'Customer_5', 'Customer_6'],
    'city': ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad',
             'Pune', 'Ahmedabad', 'Noida', 'Bangalore', 'Kolkata',
             'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Pune', 'Kolkata'],
    'capacity': [1000, 1200, 800, 2500, 2800, 2200, 3000, 3500, 2000, 1800, 1500, 0, 0, 0, 0, 0, 0],
    'demand': [0, 0, 0, 100, 120, 90, 200, 250, 300, 280, 220, 400, 350, 380, 300, 320, 280],
    'vulnerability': [0.3, 0.25, 0.35, 0.4, 0.35, 0.45, 0.3, 0.25, 0.4, 0.35, 0.5, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
}

# Create Routes Dataset
routes_data = {
    'source_id': [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 11, 11],
    'target_id': [4, 5, 4, 6, 5, 6, 7, 8, 7, 8, 7, 8, 9, 10, 11, 9, 10, 11, 12, 13, 16, 14, 15, 13, 17],
    'distance_km': [400, 800, 1000, 600, 1200, 400, 300, 500, 700, 400, 500, 600, 350, 450, 800, 500, 300, 700, 200, 150, 250, 100, 300, 400, 100],
    'transport_time_days': [2, 4, 5, 3, 6, 2, 1.5, 2.5, 3.5, 2, 2.5, 3, 1.5, 2, 4, 2.5, 1.5, 3.5, 1, 1, 1.5, 0.5, 1.5, 2, 0.5],
    'capacity': [800, 600, 700, 900, 500, 800, 1200, 1000, 900, 1100, 950, 1050, 1500, 1400, 1200, 1600, 1500, 1300, 800, 850, 700, 900, 800, 750, 850],
    'delay_probability': [0.15, 0.2, 0.18, 0.12, 0.22, 0.14, 0.1, 0.12, 0.15, 0.11, 0.13, 0.14, 0.08, 0.09, 0.14, 0.1, 0.08, 0.12, 0.05, 0.05, 0.07, 0.03, 0.06, 0.08, 0.04]
}

# Create Disruption Scenarios Dataset
disruptions_data = {
    'disruption_id': list(range(1, 21)),
    'disruption_type': ['Supplier_Delay']*3 + ['Warehouse_Overload']*3 + ['Road_Closure']*3 + ['Truck_Delay']*3 + ['Weather_Disruption']*3 + ['Demand_Surge']*3 + ['Equipment_Failure']*2,
    'affected_node_id': [1, 2, 3, 4, 5, 6, 1, 4, 7, 4, 7, 9, 4, 5, 7, 12, 13, 14, 7, 4],
    'severity': [0.5, 0.6, 0.7, 0.4, 0.5, 0.45, 0.8, 0.75, 0.7, 0.3, 0.35, 0.25, 0.55, 0.6, 0.5, 0.8, 0.75, 0.85, 0.65, 0.6],
    'duration_days': [3, 4, 5, 2, 3, 2, 7, 5, 4, 2, 2, 1, 3, 3, 2, 3, 2, 4, 6, 5],
    'description': [
        'Supplier_A production delay',
        'Supplier_B supply shortage',
        'Supplier_C material crisis',
        'Warehouse_X capacity reached',
        'Warehouse_Y congestion',
        'Warehouse_Z overstocked',
        'Road to Supplier_A blocked',
        'Road to Warehouse_X closed',
        'Road to Factory_1 damaged',
        'Truck delayed at Warehouse_X',
        'Truck delayed at Factory_1',
        'Truck delayed at DC_North',
        'Heavy rain at Warehouse_X',
        'Monsoon at Warehouse_Y',
        'Storm at Factory_1',
        'Demand surge - Customer_1',
        'Demand surge - Customer_2',
        'Demand surge - Customer_3',
        'Factory_1 equipment failure',
        'Warehouse_X conveyor failure'
    ]
}

df_nodes = pd.DataFrame(nodes_data)
df_routes = pd.DataFrame(routes_data)
df_disruptions = pd.DataFrame(disruptions_data)

print(f"✓ Generated {len(df_nodes)} nodes")
print(f"✓ Generated {len(df_routes)} routes")
print(f"✓ Generated {len(df_disruptions)} disruption scenarios")

# =============================================================================
# PHASE 2: NETWORK CONSTRUCTION
# =============================================================================
print("\n[PHASE 2] CONSTRUCTING LOGISTICS NETWORK...")

# Create Directed Graph
G = nx.DiGraph()

# Add nodes with attributes
for _, row in df_nodes.iterrows():
    G.add_node(
        row['node_id'],
        node_type=row['node_type'],
        name=row['node_name'],
        city=row['city'],
        capacity=row['capacity'],
        demand=row['demand'],
        vulnerability=row['vulnerability']
    )

# Add edges with attributes
for _, row in df_routes.iterrows():
    G.add_edge(
        row['source_id'],
        row['target_id'],
        distance=row['distance_km'],
        time=row['transport_time_days'],
        capacity=row['capacity'],
        delay_prob=row['delay_probability']
    )

print(f"✓ Network created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

# Analyze network structure
print("\nNetwork Analysis:")
print(f"  - Suppliers: {len([n for n in G.nodes() if G.nodes[n]['node_type'] == 'Supplier'])}")
print(f"  - Warehouses: {len([n for n in G.nodes() if G.nodes[n]['node_type'] == 'Warehouse'])}")
print(f"  - Factories: {len([n for n in G.nodes() if G.nodes[n]['node_type'] == 'Factory'])}")
print(f"  - Distribution Centers: {len([n for n in G.nodes() if G.nodes[n]['node_type'] == 'Distribution_Center'])}")
print(f"  - Customers: {len([n for n in G.nodes() if G.nodes[n]['node_type'] == 'Customer'])}")

# =============================================================================
# PHASE 2B: NETWORK VISUALIZATION
# =============================================================================
print("\n[PHASE 2B] VISUALIZING LOGISTICS NETWORK...")

fig, ax = plt.subplots(figsize=(16, 10))

# Use hierarchical layout
pos = {}
node_types = df_nodes['node_type'].unique()
levels = {
    'Supplier': 0,
    'Warehouse': 1,
    'Factory': 2,
    'Distribution_Center': 3,
    'Customer': 4
}

y_positions = {
    'Supplier': [0, 1, 2],
    'Warehouse': [0.5, 1.5, 2.5],
    'Factory': [0.5, 1.5],
    'Distribution_Center': [0, 1.5, 2.5],
    'Customer': [0, 0.8, 1.6, 2.4, 3.2, 4, 4.8]
}

for idx, (node_id, attrs) in enumerate(G.nodes(data=True)):
    node_type = attrs['node_type']
    level = levels[node_type]
    y_idx = df_nodes[df_nodes['node_id'] == node_id].index[0]
    
    if node_type == 'Supplier':
        y = y_positions['Supplier'][y_idx]
    elif node_type == 'Warehouse':
        y = y_positions['Warehouse'][y_idx - 3]
    elif node_type == 'Factory':
        y = y_positions['Factory'][y_idx - 6]
    elif node_type == 'Distribution_Center':
        y = y_positions['Distribution_Center'][y_idx - 8]
    else:  # Customer
        y = y_positions['Customer'][y_idx - 11]
    
    pos[node_id] = (level * 2, y)

# Node colors based on type
node_colors = []
node_sizes = []
for node in G.nodes():
    node_type = G.nodes[node]['node_type']
    if node_type == 'Supplier':
        node_colors.append('#FF6B6B')
        node_sizes.append(800)
    elif node_type == 'Warehouse':
        node_colors.append('#4ECDC4')
        node_sizes.append(800)
    elif node_type == 'Factory':
        node_colors.append('#45B7D1')
        node_sizes.append(900)
    elif node_type == 'Distribution_Center':
        node_colors.append('#FFA07A')
        node_sizes.append(800)
    else:  # Customer
        node_colors.append('#95E1D3')
        node_sizes.append(600)

# Draw network
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, ax=ax, alpha=0.9)
nx.draw_networkx_edges(G, pos, edge_color='gray', width=1.5, alpha=0.6, ax=ax, 
                       arrowsize=15, arrowstyle='->', connectionstyle="arc3,rad=0.1")
nx.draw_networkx_labels(G, pos, labels={node: G.nodes[node]['name'].split('_')[0] for node in G.nodes()},
                       font_size=7, font_weight='bold', ax=ax)

ax.set_title('Logistics Network: Supplier → Warehouse → Factory → DC → Customer', fontsize=14, fontweight='bold')
ax.axis('off')

# Add legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#FF6B6B', label='Supplier'),
    Patch(facecolor='#4ECDC4', label='Warehouse'),
    Patch(facecolor='#45B7D1', label='Factory'),
    Patch(facecolor='#FFA07A', label='Distribution Center'),
    Patch(facecolor='#95E1D3', label='Customer')
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
plt.tight_layout()
plt.savefig('logistics_network.png', dpi=300, bbox_inches='tight')
plt.show()

print("✓ Network visualization saved as 'logistics_network.png'")

# =============================================================================
# PHASE 3: CASCADE SIMULATION ENGINE
# =============================================================================
print("\n[PHASE 3] BUILDING CASCADE SIMULATION ENGINE...")

class CascadeSimulator:
    """Simulates disruption cascades through the logistics network"""
    
    def __init__(self, graph, nodes_df):
        self.graph = graph
        self.nodes_df = nodes_df
        self.affected_nodes = set()
        self.cascade_data = []
    
    def get_downstream_nodes(self, node_id):
        """Find all nodes downstream from a disrupted node"""
        downstream = set()
        try:
            descendants = nx.descendants(self.graph, node_id)
            downstream = descendants
        except:
            downstream = set()
        return downstream
    
    def calculate_impact(self, disrupted_node, severity, duration):
        """Calculate the impact of a disruption"""
        affected = self.get_downstream_nodes(disrupted_node)
        
        # Count affected customers
        affected_customers = len([n for n in affected if self.graph.nodes[n]['node_type'] == 'Customer'])
        
        # Calculate affected demand
        affected_demand = sum([self.graph.nodes[n]['demand'] for n in affected 
                             if self.graph.nodes[n]['node_type'] == 'Customer'])
        
        # Calculate critical node impact (nodes with high out-degree)
        critical_nodes = [n for n in affected if self.graph.out_degree(n) > 2]
        
        # Get disrupted node info
        disrupted_node_type = self.graph.nodes[disrupted_node]['node_type']
        disrupted_name = self.graph.nodes[disrupted_node]['name']
        disrupted_vulnerability = self.graph.nodes[disrupted_node]['vulnerability']
        
        return {
            'disrupted_node': disrupted_node,
            'disrupted_name': disrupted_name,
            'disrupted_type': disrupted_node_type,
            'severity': severity,
            'duration': duration,
            'num_affected_nodes': len(affected),
            'num_affected_customers': affected_customers,
            'affected_demand': affected_demand,
            'critical_nodes_affected': len(critical_nodes),
            'vulnerability': disrupted_vulnerability
        }
    
    def calculate_cascade_risk_score(self, impact_dict):
        """
        Calculate Cascade Risk Score (0-100)
        
        Formula:
        Risk = (Affected_Nodes_Weight × nodes_normalized +
                Affected_Customers_Weight × customers_normalized +
                Affected_Demand_Weight × demand_normalized +
                Critical_Nodes_Weight × critical_normalized +
                Vulnerability_Weight × vulnerability +
                Duration_Weight × duration_normalized) × Severity
        
        This ensures higher impact when:
        - More nodes are affected
        - More customers are affected
        - More demand is disrupted
        - Critical nodes are hit
        - Node is vulnerable
        - Disruption lasts longer
        - Severity is high
        """
        
        # Normalization factors
        max_nodes = 16
        max_customers = 6
        max_demand = 2310  # Sum of all customer demand
        max_critical = 5
        max_duration = 7
        
        # Weighted components
        nodes_score = (impact_dict['num_affected_nodes'] / max_nodes) * 20
        customers_score = (impact_dict['num_affected_customers'] / max_customers) * 25
        demand_score = (impact_dict['affected_demand'] / max_demand) * 25
        critical_score = (impact_dict['critical_nodes_affected'] / max_critical) * 15
        vulnerability_score = impact_dict['vulnerability'] * 10
        duration_score = (impact_dict['duration'] / max_duration) * 5
        
        # Combine with severity multiplier
        base_risk = nodes_score + customers_score + demand_score + critical_score + vulnerability_score + duration_score
        cascade_risk = base_risk * (1 + impact_dict['severity'])  # Severity amplifies the impact
        
        # Normalize to 0-100
        cascade_risk = min(100, cascade_risk)
        
        return cascade_risk
    
    def classify_risk(self, score):
        """Classify risk level based on score"""
        if score <= 30:
            return 'LOW'
        elif score <= 60:
            return 'MEDIUM'
        elif score <= 80:
            return 'HIGH'
        else:
            return 'CRITICAL'
    
    def simulate_disruption(self, disrupted_node, severity, duration):
        """Simulate a single disruption and calculate its cascade impact"""
        impact = self.calculate_impact(disrupted_node, severity, duration)
        risk_score = self.calculate_cascade_risk_score(impact)
        risk_level = self.classify_risk(risk_score)
        
        impact['cascade_risk_score'] = risk_score
        impact['risk_level'] = risk_level
        
        return impact

# Create simulator
simulator = CascadeSimulator(G, df_nodes)
print("✓ Cascade Simulation Engine initialized")

# =============================================================================
# PHASE 4: SCENARIO ANALYSIS
# =============================================================================
print("\n[PHASE 4] RUNNING DISRUPTION SCENARIO ANALYSIS...")

# Simulate all disruption scenarios
results = []
for _, disruption in df_disruptions.iterrows():
    result = simulator.simulate_disruption(
        disrupted_node=disruption['affected_node_id'],
        severity=disruption['severity'],
        duration=disruption['duration_days']
    )
    result['disruption_type'] = disruption['disruption_type']
    result['scenario_id'] = disruption['disruption_id']
    results.append(result)

df_results = pd.DataFrame(results)

print(f"✓ Simulated {len(results)} disruption scenarios")

# Display top 10 most dangerous disruptions
print("\nTOP 10 MOST DANGEROUS DISRUPTIONS:")
print("="*100)
top_10 = df_results.nlargest(10, 'cascade_risk_score')[['scenario_id', 'disrupted_name', 'disruption_type', 
                                                           'cascade_risk_score', 'risk_level', 'affected_demand']]
for idx, row in top_10.iterrows():
    print(f"{int(row['scenario_id']):2d}. {row['disrupted_name']:15s} ({row['disruption_type']:20s}) "
          f"| Risk: {row['cascade_risk_score']:6.1f} ({row['risk_level']:8s}) | Demand Impact: {int(row['affected_demand']):4d}")

# Risk distribution
print("\nRISK LEVEL DISTRIBUTION:")
print("="*100)
risk_counts = df_results['risk_level'].value_counts()
for level in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
    count = risk_counts.get(level, 0)
    pct = (count / len(df_results)) * 100
    print(f"  {level:10s}: {count:2d} scenarios ({pct:5.1f}%)")

# =============================================================================
# PHASE 4B: VISUALIZATIONS
# =============================================================================
print("\n[PHASE 4B] CREATING ANALYSIS VISUALIZATIONS...")

fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# 1. Risk Score Distribution
ax = axes[0, 0]
ax.hist(df_results['cascade_risk_score'], bins=15, color='#FF6B6B', alpha=0.7, edgecolor='black')
ax.axvline(df_results['cascade_risk_score'].mean(), color='darkred', linestyle='--', linewidth=2, label=f'Mean: {df_results["cascade_risk_score"].mean():.1f}')
ax.set_xlabel('Cascade Risk Score', fontweight='bold')
ax.set_ylabel('Frequency', fontweight='bold')
ax.set_title('Distribution of Cascade Risk Scores', fontweight='bold')
ax.legend()
ax.grid(alpha=0.3)

# 2. Top Disruptions by Risk
ax = axes[0, 1]
top_15 = df_results.nlargest(15, 'cascade_risk_score')
colors_map = {'LOW': '#95E1D3', 'MEDIUM': '#FFE66D', 'HIGH': '#FF6B6B', 'CRITICAL': '#8B0000'}
colors = [colors_map[level] for level in top_15['risk_level']]
ax.barh(range(len(top_15)), top_15['cascade_risk_score'], color=colors, edgecolor='black')
ax.set_yticks(range(len(top_15)))
ax.set_yticklabels([f"{name[:12]}" for name in top_15['disrupted_name']], fontsize=9)
ax.set_xlabel('Cascade Risk Score', fontweight='bold')
ax.set_title('Top 15 Highest Risk Disruptions', fontweight='bold')
ax.grid(alpha=0.3, axis='x')

# 3. Risk by Disruption Type
ax = axes[1, 0]
risk_by_type = df_results.groupby('disruption_type')['cascade_risk_score'].mean().sort_values(ascending=False)
colors_type = ['#FF6B6B' if x > 60 else '#FFE66D' if x > 30 else '#95E1D3' for x in risk_by_type.values]
ax.bar(range(len(risk_by_type)), risk_by_type.values, color=colors_type, edgecolor='black')
ax.set_xticks(range(len(risk_by_type)))
ax.set_xticklabels(risk_by_type.index, rotation=45, ha='right', fontsize=9)
ax.set_ylabel('Average Cascade Risk Score', fontweight='bold')
ax.set_title('Average Risk by Disruption Type', fontweight='bold')
ax.grid(alpha=0.3, axis='y')

# 4. Risk Level Pie Chart
ax = axes[1, 1]
risk_counts = df_results['risk_level'].value_counts()
risk_order = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
risk_counts = risk_counts.reindex(risk_order, fill_value=0)
colors_pie = ['#95E1D3', '#FFE66D', '#FF6B6B', '#8B0000']
wedges, texts, autotexts = ax.pie(risk_counts.values, labels=risk_counts.index, autopct='%1.1f%%',
                                    colors=colors_pie, startangle=90, textprops={'fontweight': 'bold'})
ax.set_title('Distribution of Risk Levels Across All Scenarios', fontweight='bold')

plt.tight_layout()
plt.savefig('cascade_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

print("✓ Analysis visualizations saved as 'cascade_analysis.png'")

# Example cascade visualization
print("\n[PHASE 4C] VISUALIZING EXAMPLE CASCADE...")

fig, ax = plt.subplots(figsize=(16, 10))

# Pick the highest risk scenario
highest_risk_scenario = df_results.loc[df_results['cascade_risk_score'].idxmax()]
disrupted_node = int(highest_risk_scenario['disrupted_node'])
affected = simulator.get_downstream_nodes(disrupted_node) | {disrupted_node}

# Node colors for cascade visualization
cascade_colors = []
for node in G.nodes():
    if node == disrupted_node:
        cascade_colors.append('#FF0000')  # Red - disrupted
    elif node in affected:
        cascade_colors.append('#FFA500')  # Orange - affected
    else:
        cascade_colors.append('#95E1D3')  # Light blue - not affected

# Draw cascade network
nx.draw_networkx_nodes(G, pos, node_color=cascade_colors, node_size=node_sizes, ax=ax, alpha=0.9)
nx.draw_networkx_edges(G, pos, edge_color='gray', width=1.5, alpha=0.6, ax=ax,
                       arrowsize=15, arrowstyle='->', connectionstyle="arc3,rad=0.1")
nx.draw_networkx_labels(G, pos, labels={node: G.nodes[node]['name'].split('_')[0] for node in G.nodes()},
                       font_size=7, font_weight='bold', ax=ax)

ax.set_title(f'Cascade Example: {highest_risk_scenario["disrupted_name"]} Disruption\n'
             f'Risk Score: {highest_risk_scenario["cascade_risk_score"]:.1f} ({highest_risk_scenario["risk_level"]})',
             fontsize=14, fontweight='bold')
ax.axis('off')

# Add legend
cascade_legend = [
    Patch(facecolor='#FF0000', label=f'Disrupted Node ({highest_risk_scenario["disrupted_name"]})'),
    Patch(facecolor='#FFA500', label=f'Affected Nodes ({len(affected)-1})'),
    Patch(facecolor='#95E1D3', label='Unaffected Nodes')
]
ax.legend(handles=cascade_legend, loc='upper left', fontsize=11)

plt.tight_layout()
plt.savefig('cascade_example.png', dpi=300, bbox_inches='tight')
plt.show()

print(f"✓ Cascade example visualization saved as 'cascade_example.png'")

# =============================================================================
# PHASE 5: MACHINE LEARNING PREPARATION
# =============================================================================
print("\n[PHASE 5] PREPARING DATA FOR MACHINE LEARNING...")

# Generate historical simulation dataset
print("Generating historical simulation dataset...")

# Extended simulations for ML training
ml_data = []
np.random.seed(42)

for _ in range(200):
    # Randomly select a node and disruption parameters
    disrupted_node = np.random.choice(df_nodes['node_id'].values)
    severity = np.random.uniform(0.1, 1.0)
    duration = np.random.randint(1, 8)
    
    impact = simulator.simulate_disruption(disrupted_node, severity, duration)
    impact['disruption_type'] = np.random.choice(df_disruptions['disruption_type'].unique())
    ml_data.append(impact)

df_ml_data = pd.DataFrame(ml_data)

# Define target variable: High-impact cascade (score > 60)
df_ml_data['is_high_impact'] = (df_ml_data['cascade_risk_score'] > 60).astype(int)

print(f"✓ Generated {len(df_ml_data)} historical simulations")
print(f"  - High-impact cascades: {df_ml_data['is_high_impact'].sum()} ({df_ml_data['is_high_impact'].mean()*100:.1f}%)")
print(f"  - Low-impact cascades: {(1-df_ml_data['is_high_impact']).sum()} ({(1-df_ml_data['is_high_impact']).mean()*100:.1f}%)")

# Feature Engineering
print("\nFeature Engineering...")

# Encode categorical variables
disruption_type_mapping = {dtype: i for i, dtype in enumerate(df_ml_data['disruption_type'].unique())}
df_ml_data['disruption_type_encoded'] = df_ml_data['disruption_type'].map(disruption_type_mapping)

# Normalize numerical features
from sklearn.preprocessing import StandardScaler

feature_columns = ['severity', 'duration', 'vulnerability', 'num_affected_nodes', 
                  'num_affected_customers', 'affected_demand', 'critical_nodes_affected', 'disruption_type_encoded']

df_ml_data_features = df_ml_data[feature_columns].copy()

scaler = StandardScaler()
df_ml_data_scaled = scaler.fit_transform(df_ml_data_features)
df_ml_data_scaled = pd.DataFrame(df_ml_data_scaled, columns=feature_columns)

target = df_ml_data['is_high_impact']

print(f"✓ Features prepared: {len(feature_columns)} features")
print(f"  Features: {feature_columns}")

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(df_ml_data_scaled, target, test_size=0.2, random_state=42, stratify=target)

print(f"\n✓ Train-Test Split:")
print(f"  - Training set: {len(X_train)} samples")
print(f"  - Test set: {len(X_test)} samples")

# =============================================================================
# PHASE 5B: MODEL TRAINING
# =============================================================================
print("\n[PHASE 5B] TRAINING MACHINE LEARNING MODELS...")

# Model 1: Logistic Regression
print("\nTraining Logistic Regression Model...")
lr_model = LogisticRegression(random_state=42, max_iter=1000)
lr_model.fit(X_train, y_train)

lr_train_acc = lr_model.score(X_train, y_train)
lr_test_acc = lr_model.score(X_test, y_test)
lr_pred = lr_model.predict(X_test)
lr_pred_proba = lr_model.predict_proba(X_test)[:, 1]

print(f"  ✓ Training Accuracy: {lr_train_acc:.3f}")
print(f"  ✓ Testing Accuracy: {lr_test_acc:.3f}")
print(f"  ✓ ROC-AUC Score: {roc_auc_score(y_test, lr_pred_proba):.3f}")

# Model 2: Decision Tree
print("\nTraining Decision Tree Model...")
dt_model = DecisionTreeClassifier(max_depth=5, random_state=42, min_samples_split=10)
dt_model.fit(X_train, y_train)

dt_train_acc = dt_model.score(X_train, y_train)
dt_test_acc = dt_model.score(X_test, y_test)
dt_pred = dt_model.predict(X_test)
dt_pred_proba = dt_model.predict_proba(X_test)[:, 1]

print(f"  ✓ Training Accuracy: {dt_train_acc:.3f}")
print(f"  ✓ Testing Accuracy: {dt_test_acc:.3f}")
print(f"  ✓ ROC-AUC Score: {roc_auc_score(y_test, dt_pred_proba):.3f}")

# =============================================================================
# PHASE 5C: MODEL EVALUATION
# =============================================================================
print("\n[PHASE 5C] MODEL EVALUATION AND INTERPRETATION...")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Model Accuracy Comparison
ax = axes[0, 0]
models = ['Logistic\nRegression', 'Decision\nTree']
train_accs = [lr_train_acc, dt_train_acc]
test_accs = [lr_test_acc, dt_test_acc]

x = np.arange(len(models))
width = 0.35

ax.bar(x - width/2, train_accs, width, label='Training Accuracy', color='#4ECDC4', edgecolor='black')
ax.bar(x + width/2, test_accs, width, label='Testing Accuracy', color='#FF6B6B', edgecolor='black')

ax.set_ylabel('Accuracy', fontweight='bold')
ax.set_title('Model Accuracy Comparison', fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(models)
ax.set_ylim([0, 1])
ax.legend()
ax.grid(alpha=0.3, axis='y')

for i, (train, test) in enumerate(zip(train_accs, test_accs)):
    ax.text(i - width/2, train + 0.02, f'{train:.2f}', ha='center', fontweight='bold')
    ax.text(i + width/2, test + 0.02, f'{test:.2f}', ha='center', fontweight='bold')

# 2. Confusion Matrix - Logistic Regression
ax = axes[0, 1]
cm_lr = confusion_matrix(y_test, lr_pred)
sns.heatmap(cm_lr, annot=True, fmt='d', cmap='Blues', ax=ax, cbar=False, 
            xticklabels=['Low Impact', 'High Impact'], yticklabels=['Low Impact', 'High Impact'])
ax.set_ylabel('True Label', fontweight='bold')
ax.set_xlabel('Predicted Label', fontweight='bold')
ax.set_title('Logistic Regression - Confusion Matrix', fontweight='bold')

# 3. Confusion Matrix - Decision Tree
ax = axes[1, 0]
cm_dt = confusion_matrix(y_test, dt_pred)
sns.heatmap(cm_dt, annot=True, fmt='d', cmap='Greens', ax=ax, cbar=False,
            xticklabels=['Low Impact', 'High Impact'], yticklabels=['Low Impact', 'High Impact'])
ax.set_ylabel('True Label', fontweight='bold')
ax.set_xlabel('Predicted Label', fontweight='bold')
ax.set_title('Decision Tree - Confusion Matrix', fontweight='bold')

# 4. Feature Importance - Decision Tree
ax = axes[1, 1]
feature_importance = dt_model.feature_importances_
feature_importance_sorted = sorted(zip(feature_columns, feature_importance), key=lambda x: x[1], reverse=True)
features_sorted, importances_sorted = zip(*feature_importance_sorted)

ax.barh(range(len(features_sorted)), importances_sorted, color='#FFA07A', edgecolor='black')
ax.set_yticks(range(len(features_sorted)))
ax.set_yticklabels(features_sorted, fontsize=9)
ax.set_xlabel('Importance', fontweight='bold')
ax.set_title('Decision Tree - Feature Importance', fontweight='bold')
ax.grid(alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('model_evaluation.png', dpi=300, bbox_inches='tight')
plt.show()

print("✓ Model evaluation visualizations saved as 'model_evaluation.png'")

# Detailed classification reports
print("\n" + "="*80)
print("LOGISTIC REGRESSION - CLASSIFICATION REPORT")
print("="*80)
print(classification_report(y_test, lr_pred, target_names=['Low Impact', 'High Impact']))

print("="*80)
print("DECISION TREE - CLASSIFICATION REPORT")
print("="*80)
print(classification_report(y_test, dt_pred, target_names=['Low Impact', 'High Impact']))

# =============================================================================
# PHASE 5D: PREDICTION ON NEW DISRUPTIONS
# =============================================================================
print("\n[PHASE 5D] PREDICTING RISK FOR NEW DISRUPTIONS...")

# Create a few new disruption scenarios
new_disruptions = [
    {'severity': 0.8, 'duration': 5, 'vulnerability': 0.4, 'num_affected_nodes': 8,
     'num_affected_customers': 4, 'affected_demand': 800, 'critical_nodes_affected': 2, 'disruption_type_encoded': 0},
    
    {'severity': 0.2, 'duration': 1, 'vulnerability': 0.2, 'num_affected_nodes': 2,
     'num_affected_customers': 1, 'affected_demand': 150, 'critical_nodes_affected': 0, 'disruption_type_encoded': 3},
    
    {'severity': 0.6, 'duration': 4, 'vulnerability': 0.5, 'num_affected_nodes': 6,
     'num_affected_customers': 3, 'affected_demand': 600, 'critical_nodes_affected': 1, 'disruption_type_encoded': 1}
]

print("Making predictions on new disruption scenarios...\n")

for i, disruption in enumerate(new_disruptions, 1):
    # Scale the features
    disruption_df = pd.DataFrame([disruption])
    disruption_scaled = scaler.transform(disruption_df)
    
    # Predict with both models
    lr_pred_result = lr_model.predict(disruption_scaled)[0]
    lr_prob = lr_model.predict_proba(disruption_scaled)[0][1]
    
    dt_pred_result = dt_model.predict(disruption_scaled)[0]
    dt_prob = dt_model.predict_proba(disruption_scaled)[0][1]
    
    print(f"Scenario {i}:")
    print(f"  Severity: {disruption['severity']:.1f} | Duration: {disruption['duration']} days | Affected Nodes: {disruption['num_affected_nodes']}")
    print(f"  Logistic Regression: {'HIGH RISK' if lr_pred_result == 1 else 'LOW RISK'} (Confidence: {lr_prob:.1%})")
    print(f"  Decision Tree:       {'HIGH RISK' if dt_pred_result == 1 else 'LOW RISK'} (Confidence: {dt_prob:.1%})")
    print()

# =============================================================================
# FINAL SUMMARY
# =============================================================================
print("\n" + "="*80)
print("LOGISTICS CASCADE FAILURE PREDICTOR - EXECUTION COMPLETE")
print("="*80)

summary_stats = {
    'Total Disruption Scenarios': len(df_results),
    'Critical Risk Scenarios': len(df_results[df_results['risk_level'] == 'CRITICAL']),
    'Average Cascade Risk Score': f"{df_results['cascade_risk_score'].mean():.1f}",
    'Maximum Risk Score': f"{df_results['cascade_risk_score'].max():.1f}",
    'ML Model Best Accuracy': f"{max(lr_test_acc, dt_test_acc):.1%}",
    'Total Nodes in Network': G.number_of_nodes(),
    'Total Edges in Network': G.number_of_edges()
}

for key, value in summary_stats.items():
    print(f"  {key}: {value}")

print("\n" + "="*80)
print("OUTPUT FILES GENERATED:")
print("="*80)
print("  1. logistics_network.png - Network visualization")
print("  2. cascade_analysis.png - Risk analysis charts")
print("  3. cascade_example.png - Example cascade visualization")
print("  4. model_evaluation.png - ML model performance")
print("\nDATASETS CREATED:")
print("  1. df_nodes - Logistics network nodes")
print("  2. df_routes - Logistics network edges/routes")
print("  3. df_disruptions - Disruption scenarios")
print("  4. df_results - Simulation results with risk scores")
print("  5. df_ml_data - Historical data for ML training")
print("\nMODELS TRAINED:")
print(f"  1. Logistic Regression (Accuracy: {lr_test_acc:.1%})")
print(f"  2. Decision Tree (Accuracy: {dt_test_acc:.1%})")
print("\n" + "="*80)
