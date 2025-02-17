class HealthManager {
    constructor() {
        // カラー設定
        this.colors = {
            weight: '#4A90E2',    // 体重: 青
            fat: '#F5A623',       // 体脂肪率: オレンジ
            fat_mass: '#FF4757',  // 体脂肪量: 赤
            lean_mass: '#2ED573', // 除脂肪体重: 緑
            bmi: '#5352ED'        // BMI: 紫
        };

        // メインチャートの設定
        this.mainChart = null;
        this.currentChartType = 'weight';
        this.currentPeriod = 'total';

        // グラフの名称と単位
        this.chartLabels = {
            weight: { name: '体重', unit: 'kg' },
            fat: { name: '体脂肪率', unit: '%' },
            fat_mass: { name: '体脂肪量', unit: 'kg' },
            lean_mass: { name: '除脂肪体重', unit: 'kg' },
            bmi: { name: 'BMI', unit: '' }
        };

        // モーダル参照
        this.recordModal = document.getElementById('recordModal');

        // 初期化
        this.initialize();
    }

    async initialize() {
        this.initializeModals();
        this.initializeCharts();
        this.initializeEventListeners();
        await this.loadData();
    }

    initializeModals() {
        // モーダルを開く
        document.getElementById('showRecordModal')?.addEventListener('click', () => {
            this.recordModal?.classList.add('active');
        });

        // モーダルを閉じる
        document.querySelectorAll('[data-close-modal]').forEach(btn => {
            btn.addEventListener('click', () => {
                this.recordModal?.classList.remove('active');
            });
        });

        // オーバーレイクリックで閉じる
        document.querySelector('.modal-overlay')?.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.recordModal?.classList.remove('active');
            }
        });
    }

    initializeCharts() {
        const ctx = document.getElementById('mainChart')?.getContext('2d');
        if (!ctx) return;

        this.mainChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    borderColor: this.colors[this.currentChartType],
                    backgroundColor: `${this.colors[this.currentChartType]}20`,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'white',
                        titleColor: '#343A40',
                        bodyColor: '#343A40',
                        borderColor: '#DEE2E6',
                        borderWidth: 1,
                        padding: 10,
                        callbacks: {
                            label: (context) => {
                                const label = this.chartLabels[this.currentChartType];
                                return `${context.raw}${label.unit}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false }
                    },
                    y: {
                        beginAtZero: false,
                        grid: { color: '#F8F9FA' }
                    }
                }
            }
        });
    }

    initializeEventListeners() {
        // 期間選択
        document.querySelectorAll('.period-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelector('.period-btn.active')?.classList.remove('active');
                btn.classList.add('active');
                this.currentPeriod = btn.dataset.period;
                this.loadData();
            });
        });

        // グラフタイプ選択
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelector('.tab-btn.active')?.classList.remove('active');
                btn.classList.add('active');
                this.currentChartType = btn.dataset.chart;
                this.updateChartType();
            });
        });
    }

    async loadData() {
        try {
            const response = await fetch(`/weight/data?period=${this.currentPeriod}`);
            const data = await response.json();
            this.updateChart(data);
        } catch (error) {
            console.error('データの読み込みに失敗しました:', error);
        }
    }

    updateChart(data) {
        if (!this.mainChart || !data.labels) return;

        const dataMap = {
            weight: data.weights,
            fat: data.bodyFat,
            fat_mass: data.fatMass,
            lean_mass: data.leanMass,
            bmi: data.bmi
        };

        const chartData = dataMap[this.currentChartType];
        const label = this.chartLabels[this.currentChartType];

        this.mainChart.data.labels = data.labels;
        this.mainChart.data.datasets[0].data = chartData;
        this.mainChart.data.datasets[0].label = label.name;
        this.mainChart.options.scales.y.title = { display: true, text: label.unit };
        
        this.mainChart.update();
    }

    updateChartType() {
        if (!this.mainChart) return;

        const color = this.colors[this.currentChartType];
        this.mainChart.data.datasets[0].borderColor = color;
        this.mainChart.data.datasets[0].backgroundColor = `${color}20`;
        
        this.loadData();
    }
}

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    window.healthManager = new HealthManager();
});