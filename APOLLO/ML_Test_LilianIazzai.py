import pickle
import pandas as pd
from sklearn.preprocessing import LabelEncoder, label_binarize, StandardScaler, Normalizer
import numpy as np
import plotly.express as px
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
import seaborn as sns
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from sklearn.metrics import roc_auc_score, f1_score, top_k_accuracy_score, roc_curve, auc

file_path = "mini_gm_public_v0.1.p"

with open(file_path, "rb") as f:
    data = pickle.load(f)
    
rows = []

for syndrome_id, subjects in data.items():
    for subject_id, images in subjects.items():
        for image_id, embedding in images.items():
            rows.append({
                "syndrome_id": syndrome_id,
                "subject_id": subject_id,
                "image_id": image_id,
                "embedding": embedding
            })

df = pd.DataFrame(rows)

df.head()
print("Data Information\n", df.info())
df['syndrome_id'] = df['syndrome_id'].astype('category')
df['image_id'] = pd.to_numeric(df['image_id'])  
df['subject_id'] = pd.to_numeric(df['subject_id'])
print("Size of embeddings: ", df['embedding'].apply(len).unique())
df = df.drop_duplicates(subset=['syndrome_id', 'subject_id', 'image_id']) 

#verifying unbalanced data
df['syndrome_id'].value_counts().plot(kind='bar')
plt.title('Target Variable Distribution')
plt.xlabel('syndrome_id')
plt.ylabel('Contagem')
plt.show()

print("Images per Syndrome\n", df['syndrome_id'].value_counts())

X = np.array(df["embedding"].tolist())
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df["syndrome_id"])

# t-SNE
palette = px.colors.qualitative.Safe  

tsne = TSNE(n_components=2, random_state=42)  
X_tsne = tsne.fit_transform(X)

fig = px.scatter(
    x=X_tsne[:, 0],
    y=X_tsne[:, 1],
    color=y,
    color_discrete_sequence=palette  
)

fig.update_layout(
    title="2D Embeddings (t-SNE)",
    xaxis_title="First t-SNE",
    yaxis_title="Second t-SNE",
    title_font=dict(size=20, family="Arial", color="darkblue"),
    paper_bgcolor="white",
    plot_bgcolor="rgba(240, 240, 240, 0.8)", 
    font=dict(size=14),
    margin=dict(l=20, r=20, t=40, b=20), 
)

fig.update_traces(marker=dict(size=8, line=dict(width=1, color="black")))

fig.show()

#KNN
smote = SMOTE()
X_resampled, y_resampled = smote.fit_resample(X, y)
scalers = {'StandardScaler': StandardScaler(), 'Normalizer': Normalizer()}
datasets = {'Balanced': (X_resampled, y_resampled), 'Unbalanced': (X, y)}
i_values = [i for i in range(1, 16)]
metrics = {'euclidean', 'cosine'}
results = {'accuracy': {}, 'roc_auc': {}, 'f1_score': {}, 'top_k': {}}

for dataset_name, (X_data, y_data) in datasets.items():
    for scaler_name, scaler in scalers.items():
        for metric in metrics:
            acc_scores = []
            f1_scores = []
            top_k_scores = []

            for i in i_values:
                pipeline = Pipeline([
                    ('scaler', scaler),
                    ('knn', KNeighborsClassifier(metric=metric, weights='distance', n_neighbors=i))
                ])

                skf = StratifiedKFold(n_splits=10)
                acc_temp = []
                f1_temp = []
                top_k_temp = []

                for train_index, test_index in skf.split(X_data, y_data):
                    X_train, X_test = X_data[train_index], X_data[test_index]
                    y_train, y_test = y_data[train_index], y_data[test_index]

                    # Training
                    pipeline.fit(X_train, y_train)
                    y_pred = pipeline.predict(X_test)
                    y_pred_proba = pipeline.predict_proba(X_test)

                    acc_temp.append(pipeline.score(X_test, y_test))
                    f1_temp.append(f1_score(y_test, y_pred, average="macro"))
                    top_k_temp.append(top_k_accuracy_score(y_test, y_pred_proba, k=5))

                acc_scores.append(np.mean(acc_temp))
                f1_scores.append(np.mean(f1_temp))
                top_k_scores.append(np.mean(top_k_temp))

            results['accuracy'][(dataset_name, scaler_name, metric)] = acc_scores
            results['f1_score'][(dataset_name, scaler_name, metric)] = f1_scores
            results['top_k'][(dataset_name, scaler_name, metric)] = top_k_scores

for dataset_name, (X_data, y_data) in datasets.items():
    for scaler_name, scaler in scalers.items():
        for metric in metrics:
            plt.figure(figsize=(10, 6))
            sns.lineplot(x=i_values, y=results['accuracy'][(dataset_name, scaler_name, metric)], marker='o', label='Accuracy')
            sns.lineplot(x=i_values, y=results['f1_score'][(dataset_name, scaler_name, metric)], marker='o', label='F1 Score')
            sns.lineplot(x=i_values, y=results['top_k'][(dataset_name, scaler_name, metric)], marker='o', label='Top-5 Accuracy')

            plt.title(f"KNN {metric.capitalize()}: {dataset_name} Data and {scaler_name}")
            plt.xlabel("K values")
            plt.ylabel("Score")
            plt.legend()
            plt.show()

# AUC
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_resampled)

n_neighbors = 2
metric = "cosine"
knn = KNeighborsClassifier(n_neighbors=n_neighbors, weights='distance', metric=metric)

kf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

y_binarized = label_binarize(y_resampled, classes=np.unique(y_resampled))
n_classes = y_binarized.shape[1]

fpr = {i: [] for i in range(n_classes)}
tpr = {i: [] for i in range(n_classes)}
roc_auc = {i: [] for i in range(n_classes)}

for train_index, test_index in kf.split(X_scaled, y_resampled):
    X_train, X_test = X_scaled[train_index], X_scaled[test_index]
    y_train, y_test = y_binarized[train_index], y_binarized[test_index]

    knn.fit(X_train, np.argmax(y_train, axis=1))
    y_score = knn.predict_proba(X_test)

    for i in range(n_classes):
        fpr_temp, tpr_temp, _ = roc_curve(y_test[:, i], y_score[:, i])
        fpr[i].append(fpr_temp)
        tpr[i].append(tpr_temp)
        roc_auc[i].append(auc(fpr_temp, tpr_temp))

mean_fpr = np.linspace(0, 1, 100)
plt.figure(figsize=(10, 8))

for i in range(n_classes):
    mean_tpr = np.mean([np.interp(mean_fpr, fpr[i][j], tpr[i][j]) for j in range(len(fpr[i]))], axis=0)
    mean_tpr[-1] = 1.0  
    mean_auc = np.mean(roc_auc[i])
    std_auc = np.std(roc_auc[i])

    plt.plot(mean_fpr, mean_tpr, label=f"Classe {i} (AUC = {mean_auc:.2f} ± {std_auc:.2f})")

plt.plot([0, 1], [0, 1], "k--", lw=2)
plt.xlabel("False Positive Rate (FPR)")
plt.ylabel("True Positive Rate (TPR)")
plt.title("ROC Curves - KNN Cosine (Balanced and Scaled)")
plt.legend(loc="lower right")
plt.grid()
plt.show()

metric = "euclidian"

for train_index, test_index in kf.split(X_scaled, y_resampled):
    X_train, X_test = X_scaled[train_index], X_scaled[test_index]
    y_train, y_test = y_binarized[train_index], y_binarized[test_index]

    knn.fit(X_train, np.argmax(y_train, axis=1))
    y_score = knn.predict_proba(X_test)

    for i in range(n_classes):
        fpr_temp, tpr_temp, _ = roc_curve(y_test[:, i], y_score[:, i])
        fpr[i].append(fpr_temp)
        tpr[i].append(tpr_temp)
        roc_auc[i].append(auc(fpr_temp, tpr_temp))

mean_fpr = np.linspace(0, 1, 100)
plt.figure(figsize=(10, 8))

for i in range(n_classes):
    mean_tpr = np.mean([np.interp(mean_fpr, fpr[i][j], tpr[i][j]) for j in range(len(fpr[i]))], axis=0)
    mean_tpr[-1] = 1.0  
    mean_auc = np.mean(roc_auc[i])
    std_auc = np.std(roc_auc[i])

    plt.plot(mean_fpr, mean_tpr, label=f"Classe {i} (AUC = {mean_auc:.2f} ± {std_auc:.2f})")

plt.plot([0, 1], [0, 1], "k--", lw=2)
plt.xlabel("False Positive Rate (FPR)")
plt.ylabel("True Positive Rate (TPR)")
plt.title("ROC Curves - KNN Euclidian (Balanced and Scaled)")
plt.legend(loc="lower right")
plt.grid()
plt.show()