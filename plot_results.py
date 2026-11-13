import matplotlib.pyplot as plt

workers = [1, 2, 3, 4]
times = [11.80, 6.72, 6.85, 5.74]
speedup = [times[0] / t for t in times]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Графік 1: Час виконання
ax1.plot(workers, times, marker='o', linewidth=2, color='#1f77b4', label='Реальний час (с)')
ax1.set_title('Залежність часу виконання від кількості воркерів')
ax1.set_xlabel('Кількість воркерів (N)')
ax1.set_ylabel('Час виконання (секунди)')
ax1.set_xticks(workers)
ax1.grid(True, linestyle='--', alpha=0.7)
for x, y in zip(workers, times):
    ax1.annotate(f"{y:.2f}s", (x, y), textcoords="offset points", xytext=(0, 8), ha='center')

# Графік 2: Прискорення (Speedup)
ax2.plot(workers, speedup, marker='s', linewidth=2, color='#2ca02c', label='Реальне прискорення')
ax2.plot(workers, workers, linestyle='--', color='gray', label='Ідеальне лінійне прискорення')
ax2.set_title('Прискорення алгоритму (Speedup)')
ax2.set_xlabel('Кількість воркерів (N)')
ax2.set_ylabel('Прискорення S(N) = T(1) / T(N)')
ax2.set_xticks(workers)
ax2.legend()
ax2.grid(True, linestyle='--', alpha=0.7)
for x, y in zip(workers, speedup):
    ax2.annotate(f"{y:.2f}x", (x, y), textcoords="offset points", xytext=(0, 8), ha='center')

plt.tight_layout()
plt.savefig('speedup_chart.png', dpi=150)
print("Графік збережено у файл speedup_chart.png")