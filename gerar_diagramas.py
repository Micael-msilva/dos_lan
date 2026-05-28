import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ════════════════════════════════════════════
# DIAGRAMA 1: Fluxo de pacotes (DoS vs MitM)
# ════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(14, 16))
ax.set_xlim(0, 14)
ax.set_ylim(0, 18)
ax.axis('off')
fig.patch.set_facecolor('white')

C = {
    'gray':   ('#F1EFE8', '#5F5E5A', '#2C2C2A'),
    'blue':   ('#E6F1FB', '#185FA5', '#0C447C'),
    'purple': ('#EEEDFE', '#534AB7', '#26215C'),
    'coral':  ('#FAECE7', '#993C1D', '#4A1B0C'),
    'teal':   ('#E1F5EE', '#0F6E56', '#04342C'),
    'amber':  ('#FAEEDA', '#854F0B', '#412402'),
    'red':    ('#FCEBEB', '#A32D2D', '#501313'),
    'green':  ('#EAF3DE', '#3B6D11', '#173404'),
}

def box(ax, x, y, w, h, line1, line2=None, color='gray', lw=1.2):
    fc, ec, tc = C[color]
    rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0,rounding_size=0.15",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3)
    ax.add_patch(rect)
    if line2:
        ax.text(x, y + 0.13, line1, ha='center', va='center', fontsize=9,
                fontweight='bold', color=tc, zorder=4)
        ax.text(x, y - 0.15, line2, ha='center', va='center', fontsize=7.5,
                color=C[color][1], zorder=4)
    else:
        ax.text(x, y, line1, ha='center', va='center', fontsize=9,
                fontweight='bold', color=tc, zorder=4)

def section_bar(ax, y, label, color):
    fc, ec, tc = C[color]
    rect = FancyBboxPatch((0.3, y - 0.22), 11.4, 0.44,
        boxstyle="round,pad=0,rounding_size=0.1",
        facecolor=fc, edgecolor=ec, linewidth=1, zorder=2)
    ax.add_patch(rect)
    ax.text(6, y, label, ha='center', va='center', fontsize=9.5,
            fontweight='bold', color=tc, zorder=3)

def arr(ax, x1, y1, x2, y2, color='#888780', dashed=False, lw=1.4):
    ls = (0, (5, 3)) if dashed else 'solid'
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle='->', color=color, lw=lw, linestyle=ls),
        zorder=4)

def lbl(ax, x, y, t, color='#5F5E5A', size=7.5, ha='center', bold=False):
    ax.text(x, y, t, ha=ha, va='center', fontsize=size, color=color,
            fontweight='bold' if bold else 'normal', zorder=5)

# SECTION 1: ANTES
section_bar(ax, 16.5, 'Antes do ataque — comunicação legítima', 'gray')

box(ax, 2.2, 15.7, 2.4, 0.65, 'Vítima', 'MAC: AA:BB:CC', color='blue')
box(ax, 7.0, 15.7, 2.4, 0.65, 'Switch', 'tabela MAC limpa', color='gray')
box(ax, 11.8, 15.7, 2.4, 0.65, 'Roteador', 'MAC: 11:22:33', color='teal')

arr(ax, 3.4, 15.82, 5.8, 15.82, color=C['teal'][1])
arr(ax, 8.2, 15.58, 3.4, 15.58, color=C['blue'][1])
arr(ax, 8.2, 15.82, 10.6, 15.82, color=C['teal'][1])
arr(ax, 10.6, 15.58, 8.2, 15.58, color=C['blue'][1])
lbl(ax, 7.0, 16.0, 'pacotes → internet', color=C['teal'][1])
lbl(ax, 7.0, 15.38, 'respostas ← internet', color=C['blue'][1])

box(ax, 7.0, 14.75, 3.8, 0.6, 'Tabela ARP da vítima', 'gateway → MAC: 11:22:33  ✓', color='blue')

# SECTION 2: ENVENENAMENTO
section_bar(ax, 13.5, 'Fase de envenenamento — ARP Replies falsos contínuos', 'coral')

box(ax, 2.2, 12.7, 2.2, 0.65, 'Vítima', 'MAC: AA:BB:CC', color='blue')
box(ax, 7.0, 12.7, 2.4, 0.65, 'Atacante', 'MAC: EE:FF:00', color='coral', lw=1.8)
box(ax, 11.8, 12.7, 2.2, 0.65, 'Roteador', 'MAC: 11:22:33', color='teal')

arr(ax, 3.4, 12.78, 5.8, 12.78, color=C['coral'][1], dashed=True, lw=1.6)
lbl(ax, 4.6, 13.0, '"gateway = EE:FF:00"', color=C['coral'][1], bold=True)
lbl(ax, 4.6, 12.58, 'ARP Reply falso', color=C['coral'][1], size=7)

arr(ax, 8.2, 12.62, 10.6, 12.62, color=C['coral'][1], dashed=True, lw=1.6)
lbl(ax, 9.4, 12.4, '"vítima = EE:FF:00"', color=C['coral'][1], bold=True)
lbl(ax, 9.4, 12.8, 'ARP Reply falso', color=C['coral'][1], size=7)

box(ax, 7.0, 11.75, 4.0, 0.6, 'Tabela ARP envenenada', 'gateway → MAC: EE:FF:00  ✗', color='red')

# SECTION 3: DoS vs MitM side by side
section_bar(ax, 10.2, 'Resultado do ataque', 'purple')

# --- DoS ---
fc, ec, tc = C['red']
rect = FancyBboxPatch((0.5, 6.2), 6.2, 3.6,
    boxstyle="round,pad=0,rounding_size=0.15",
    facecolor='#FFF5F5', edgecolor=ec, linewidth=1.2, zorder=2)
ax.add_patch(rect)
lbl(ax, 3.6, 9.6, 'Modo DoS — ip_forward = 0', color=tc, size=9, bold=True)

box(ax, 1.8, 8.8, 1.9, 0.6, 'Vítima', 'envia pacote', color='blue')
box(ax, 3.6, 8.8, 2.0, 0.6, 'Atacante', 'descarta tudo', color='coral', lw=1.8)
box(ax, 1.8, 7.2, 1.9, 0.6, 'Roteador', 'não recebe nada', color='gray')

arr(ax, 2.8, 8.8, 2.9, 8.8, color=C['red'][1], lw=1.4)

# X symbol
ax.plot([3.6, 3.6], [8.5, 8.1], color=C['red'][1], lw=1.5, zorder=4)
ax.plot([3.3, 3.9], [8.1, 7.7], color=C['red'][1], lw=2.2, zorder=4)
ax.plot([3.9, 3.3], [8.1, 7.7], color=C['red'][1], lw=2.2, zorder=4)
lbl(ax, 4.7, 7.9, 'pacote descartado', color=C['red'][1], size=7.5)

# Roteador view
rect2 = FancyBboxPatch((0.7, 6.3), 2.8, 0.5,
    boxstyle="round,pad=0,rounding_size=0.1",
    facecolor=C['amber'][0], edgecolor=C['amber'][1], linewidth=0.8, zorder=3)
ax.add_patch(rect2)
lbl(ax, 2.1, 6.55, 'Roteador: "a vítima sumiu"', color=C['amber'][2], size=7.2)

# --- MitM ---
fc, ec, tc = C['teal']
rect3 = FancyBboxPatch((7.3, 6.2), 6.2, 3.6,
    boxstyle="round,pad=0,rounding_size=0.15",
    facecolor='#F0FBF7', edgecolor=ec, linewidth=1.2, zorder=2)
ax.add_patch(rect3)
lbl(ax, 10.4, 9.6, 'Modo MitM — ip_forward = 1', color=tc, size=9, bold=True)

box(ax, 8.6, 8.8, 1.9, 0.6, 'Vítima', 'envia pacote', color='blue')
box(ax, 10.4, 8.8, 2.2, 0.7, 'Atacante', 'lê e repassa', color='coral', lw=1.8)
box(ax, 8.6, 7.2, 1.9, 0.6, 'Roteador', 'recebe normal', color='teal')

arr(ax, 9.5, 8.8, 9.6, 8.8, color=C['teal'][1], lw=1.4)
lbl(ax, 9.55, 9.05, '① chega', color=C['coral'][1], size=7.2)

# Curved path: attacker → router
ax.annotate('', xy=(8.6, 7.5), xytext=(10.4, 8.5),
    arrowprops=dict(arrowstyle='->', color=C['teal'][1], lw=1.4,
                    connectionstyle='arc3,rad=-0.35'), zorder=4)
lbl(ax, 9.8, 7.7, '② reencaminha', color=C['teal'][1], size=7.2)

# Roteador view
rect4 = FancyBboxPatch((7.5, 6.3), 3.2, 0.5,
    boxstyle="round,pad=0,rounding_size=0.1",
    facecolor=C['green'][0], edgecolor=C['green'][1], linewidth=0.8, zorder=3)
ax.add_patch(rect4)
lbl(ax, 9.1, 6.55, 'Roteador: "tráfego normal"', color=C['green'][2], size=7.2)

# LEGEND
lbl(ax, 1.2, 5.2, 'Legenda:', size=8.5, bold=True, color='#2C2C2A')
items = [
    ('blue',   'Vítima'),
    ('coral',  'Atacante'),
    ('teal',   'Roteador / MitM'),
    ('red',    'Modo DoS'),
    ('amber',  'Impacto percebido'),
    ('green',  'Tráfego aparente normal'),
]
for i, (c, label) in enumerate(items):
    col = i % 3
    row = i // 3
    bx = 0.6 + col * 4.4
    by = 4.8 - row * 0.45
    rect = FancyBboxPatch((bx, by - 0.13), 0.32, 0.26,
        boxstyle="round,pad=0,rounding_size=0.06",
        facecolor=C[c][0], edgecolor=C[c][1], linewidth=0.8, zorder=3)
    ax.add_patch(rect)
    ax.text(bx + 0.48, by, label, fontsize=7.5, va='center', color='#444441')

# ARP legend
ax.annotate('', xy=(1.4, 3.7), xytext=(0.6, 3.7),
    arrowprops=dict(arrowstyle='->', color=C['coral'][1], lw=1.5,
                    linestyle=(0, (5,3))), zorder=4)
lbl(ax, 3.0, 3.7, 'ARP Reply falso (envenenamento)', color=C['coral'][1], size=7.5, ha='left')

ax.annotate('', xy=(8.4, 3.7), xytext=(7.6, 3.7),
    arrowprops=dict(arrowstyle='->', color=C['teal'][1], lw=1.5), zorder=4)
lbl(ax, 10.0, 3.7, 'Tráfego reencaminhado (MitM)', color=C['teal'][1], size=7.5, ha='left')

plt.title('Fluxo de pacotes na rede — ARP Spoofing DoS vs MitM',
    fontsize=11.5, fontweight='bold', color='#1F3864', pad=12)
plt.tight_layout(pad=0.3)
plt.savefig('/home/secret/Desktop/dos_lan/fluxo_dos_vs_mitm.png', dpi=160, bbox_inches='tight',
    facecolor='white', edgecolor='none')
print("✓ fluxo_dos_vs_mitm.png gerado")
plt.close()

# ════════════════════════════════════════════
# DIAGRAMA 2: Fluxo de operação do script
# ════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(12, 18))
ax.set_xlim(0, 12)
ax.set_ylim(0, 18)
ax.axis('off')
fig.patch.set_facecolor('white')

# Color palette
C = {
    'gray':   ('#F1EFE8', '#5F5E5A', '#2C2C2A'),
    'blue':   ('#E6F1FB', '#185FA5', '#0C447C'),
    'purple': ('#EEEDFE', '#534AB7', '#26215C'),
    'coral':  ('#FAECE7', '#993C1D', '#4A1B0C'),
    'teal':   ('#E1F5EE', '#0F6E56', '#04342C'),
    'amber':  ('#FAEEDA', '#854F0B', '#412402'),
    'red':    ('#FCEBEB', '#A32D2D', '#501313'),
}

def box(ax, x, y, w, h, label, sublabel=None, color='gray', radius=0.18, pill=False):
    fc, ec, tc = C[color]
    r = h/2 if pill else radius
    rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
        boxstyle=f"round,pad=0,rounding_size={r}",
        facecolor=fc, edgecolor=ec, linewidth=1.2, zorder=3)
    ax.add_patch(rect)
    if sublabel:
        ax.text(x, y + 0.13, label, ha='center', va='center', fontsize=9,
                fontweight='bold', color=tc, zorder=4)
        ax.text(x, y - 0.17, sublabel, ha='center', va='center', fontsize=7.5,
                color=C[color][1], zorder=4)
    else:
        ax.text(x, y, label, ha='center', va='center', fontsize=9,
                fontweight='bold', color=tc, zorder=4)

def arrow(ax, x1, y1, x2, y2, color='#888780'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle='->', color=color, lw=1.3),
        zorder=2)

def label_arrow(ax, x, y, text, ha='center', color='#5F5E5A'):
    ax.text(x, y, text, ha=ha, va='center', fontsize=7.5, color=color, zorder=5)

# Start
box(ax, 6, 17.4, 3.2, 0.55, 'Início  (execução como root)', color='gray', pill=True)
arrow(ax, 6, 17.12, 6, 16.6)

# Seleção modo
box(ax, 6, 16.2, 4.5, 0.7, 'Selecionar modo de ataque', '--forward  ou  --no-forward', color='purple')
arrow(ax, 3.75, 16.2, 2.0, 16.2, color=C['red'][1])
arrow(ax, 8.25, 16.2, 10.0, 16.2, color=C['teal'][1])

# DoS / MitM boxes
box(ax, 1.5, 16.2, 1.1, 0.65, 'Modo DoS', 'ip_forward=0', color='red')
box(ax, 10.5, 16.2, 1.1, 0.65, 'Modo MitM', 'ip_forward=1', color='teal')

label_arrow(ax, 2.7, 16.46, '--no-forward', color=C['red'][1])
label_arrow(ax, 9.3, 16.46, '--forward', color=C['teal'][1])

# Converge
ax.plot([1.5, 1.5], [15.87, 15.4], color='#B4B2A9', lw=1.2, zorder=2)
ax.plot([10.5, 10.5], [15.87, 15.4], color='#B4B2A9', lw=1.2, zorder=2)
ax.plot([1.5, 10.5], [15.4, 15.4], color='#B4B2A9', lw=1.2, zorder=2)
arrow(ax, 6, 15.4, 6, 14.9)

# Mapear rede
box(ax, 6, 14.55, 5, 0.7, 'Mapear rede local', 'interface · IP · netmask · gateway', color='blue')
arrow(ax, 6, 14.2, 6, 13.7)

# Varredura ARP
box(ax, 6, 13.35, 5, 0.7, 'Varredura ARP inicial', 'ARP broadcast → hosts ativos na sub-rede', color='blue')
arrow(ax, 6, 13.0, 6, 12.5)

# Filtrar
box(ax, 6, 12.15, 4.8, 0.7, 'Filtrar alvos válidos', 'remove gateway e IP próprio', color='gray')
arrow(ax, 6, 11.8, 6, 11.3)

# Salvar IPs
box(ax, 6, 10.95, 3.8, 0.65, 'Salvar alvos em ips.txt', color='gray')
arrow(ax, 6, 10.62, 6, 10.12)

# 3 threads
box(ax, 6, 9.8, 5.8, 0.65, 'Iniciar 3 threads paralelas', color='purple')

# Branch to threads
ax.annotate('', xy=(2.5, 9.1), xytext=(4.1, 9.47),
    arrowprops=dict(arrowstyle='->', color=C['purple'][1], lw=1.2), zorder=2)
arrow(ax, 6, 9.47, 6, 9.1)
ax.annotate('', xy=(9.5, 9.1), xytext=(7.9, 9.47),
    arrowprops=dict(arrowstyle='->', color=C['purple'][1], lw=1.2), zorder=2)

# Thread boxes
box(ax, 2.5, 8.7, 3.0, 0.72, 'Thread 1', 'Monitor novos hosts (10s)', color='purple')
box(ax, 6,   8.7, 3.0, 0.72, 'Thread 2', 'Health check spoof (8s)', color='purple')
box(ax, 9.5, 8.7, 3.0, 0.72, 'Thread 3 — main', 'arpspoof por alvo', color='purple')

# Thread 3 → arpspoof detail
arrow(ax, 9.5, 8.34, 9.5, 7.85)
box(ax, 9.5, 7.5, 3.0, 0.72, 'arpspoof -i <iface>', '-t <alvo> <gateway>', color='coral')

# Thread 2 → health check detail
arrow(ax, 6, 8.34, 6, 7.85)
box(ax, 6, 7.5, 3.2, 0.72, 'Verificar envenenamento', 'MAC gateway = nosso MAC?', color='teal')

# Thread 1 → new host detail
arrow(ax, 2.5, 8.34, 2.5, 7.85)
box(ax, 2.5, 7.5, 3.0, 0.72, 'Novo host?', 'adiciona ao set → ips.txt', color='blue')

# Converge to interrupt
ax.plot([2.5, 2.5], [7.14, 6.6], color='#B4B2A9', lw=1.2, zorder=2)
ax.plot([6.0, 6.0], [7.14, 6.6], color='#B4B2A9', lw=1.2, zorder=2)
ax.plot([9.5, 9.5], [7.14, 6.6], color='#B4B2A9', lw=1.2, zorder=2)
ax.plot([2.5, 9.5], [6.6, 6.6], color='#B4B2A9', lw=1.2, zorder=2)
arrow(ax, 6, 6.6, 6, 6.15)

# KeyboardInterrupt
box(ax, 6, 5.85, 4.8, 0.65, 'Ctrl+C → encerrar processos arpspoof', color='amber')
arrow(ax, 6, 5.52, 6, 5.02)

# End
box(ax, 6, 4.7, 3.2, 0.55, 'Rede restaurada', color='gray', pill=True)

# Legend
legend_y = 3.9
ax.text(1.2, legend_y + 0.3, 'Legenda', fontsize=8, fontweight='bold', color='#2C2C2A')
items = [
    ('gray',   'Início / fim / estrutura'),
    ('purple', 'Controle de fluxo / threads'),
    ('blue',   'Operações de rede'),
    ('teal',   'MitM / verificação'),
    ('coral',  'Ataque ativo'),
    ('amber',  'Encerramento'),
    ('red',    'Modo DoS'),
]
for i, (c, label) in enumerate(items):
    col = i % 4
    row = i // 4
    bx = 0.7 + col * 2.8
    by = legend_y - row * 0.38
    rect = FancyBboxPatch((bx, by - 0.12), 0.3, 0.24,
        boxstyle="round,pad=0,rounding_size=0.06",
        facecolor=C[c][0], edgecolor=C[c][1], linewidth=0.8)
    ax.add_patch(rect)
    ax.text(bx + 0.42, by, label, fontsize=7.2, va='center', color='#444441')

plt.title('Fluxo de operação do script — ARP Spoofing DoS/MitM',
    fontsize=11, fontweight='bold', color='#1F3864', pad=10)
plt.tight_layout(pad=0.3)
plt.savefig('/home/secret/Desktop/dos_lan/fluxo_script.png', dpi=160, bbox_inches='tight',
    facecolor='white', edgecolor='none')
print("✓ fluxo_script.png gerado")
plt.close()

print("\n✓ Ambos os diagramas foram gerados com sucesso!")
