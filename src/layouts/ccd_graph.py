import pyqtgraph as pg

def ccdGraphStyles(ccd_graph_widget: pg.PlotWidget):
    """
    Configurações de estilo para o gráfico do CCD.
    """

    # Configurações de estilo do gráfico
    ccd_graph_widget.setBackground('w')  # Fundo branco

    # Eixos
    ccd_graph_widget.getAxis('bottom').setPen('k')  # Eixo X preto
    ccd_graph_widget.getAxis('left').setPen('k')    # Eixo Y preto

    ccd_graph_widget.getAxis('bottom').setTextPen('k')  # Texto do eixo X preto
    ccd_graph_widget.getAxis('left').setTextPen('k')    # Texto do eixo Y preto

    ccd_graph_widget.setLabel('left', 'Intensidade')
    ccd_graph_widget.setLabel('bottom', 'Pixel')
    ccd_graph_widget.setTitle('Espectro CCD')