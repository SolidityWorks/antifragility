import {useEffect, useState, } from 'react'
import './App.css'
import 'chartjs-adapter-date-fns'
import {
    Chart as ChartJS,
    Legend,
    LinearScale,
    LogarithmicScale,
    LineElement,
    PointElement,
    TimeScale,
    Title,
    Tooltip,
} from 'chart.js'
import {Scatter} from "react-chartjs-2";
// import {useSearchParams} from "react-router-dom";

ChartJS.register(
    LinearScale,
    LogarithmicScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    TimeScale
)

const options = {
    showLine: true,
    scales: {
        x: {
            type: 'time' as const,
        },
        y: {
            type: 'linear' as const,
        },
    },
}

const evtSource = new EventSource("http://127.0.0.1:8008/ssf/USDT,BUSD/RUB")

evtSource.onopen = (/*e*/) => console.log("Connected."/*, e*/)

evtSource.addEventListener("ping", (event) => console.log(`ping: ${event.data}`))

evtSource.onerror = () => console.error("EventSource failed:")

const pairs = {
    1: ['USDT','RUB',false],
    2: ['BTC','RUB',false],
    3: ['ETH','RUB',false],
    4: ['BNB','RUB',false],
    5: ['BUSD','RUB',false],
    6: ['RUB','RUB',false],
    7: ['SHIB','RUB',false],
    8: ['USDT','USD',false],
    9: ['BTC','USD',false],
    10: ['ETH','USD',false],
    11: ['BNB','USD',false],
    12: ['BUSD','USD',false],
    13: ['SOL','USD',false],
    14: ['DAI','USD',false],
    15: ['USDT','EUR',false],
    16: ['BTC','EUR',false],
    17: ['ETH','EUR',false],
    18: ['BNB','EUR',false],
    19: ['BUSD','EUR',false],
    20: ['SHIB','EUR',false],
    21: ['DAI','EUR',false],
    22: ['USDT','TRY',false],
    23: ['BTC','TRY',false],
    24: ['ETH','TRY',false],
    25: ['BNB','TRY',false],
    26: ['BUSD','TRY',false],
    27: ['ADA','TRY',false],
    28: ['TRX','TRY',false],
    29: ['SHIB','TRY',false],
    30: ['SOL','TRY',false],
    31: ['DOGE','TRY',false],
    32: ['DOT','TRY',false],
    33: ['USDT','RUB',true],
    34: ['BTC','RUB',true],
    35: ['ETH','RUB',true],
    36: ['BNB','RUB',true],
    37: ['BUSD','RUB',true],
    38: ['RUB','RUB',true],
    39: ['ADA','RUB',true],
    40: ['SHIB','RUB',true],
    41: ['XRP','RUB',true],
    42: ['DAI','RUB',true],
    43: ['USDT','USD',true],
    44: ['BTC','USD',true],
    45: ['ETH','USD',true],
    46: ['BNB','USD',true],
    47: ['BUSD','USD',true],
    48: ['ADA','USD',true],
    49: ['TRX','USD',true],
    50: ['MATIC','USD',true],
    51: ['XRP','USD',true],
    52: ['SOL','USD',true],
    53: ['WRX','USD',true],
    54: ['DAI','USD',true],
    55: ['DOGE','USD',true],
    56: ['DOT','USD',true],
    57: ['USDT','EUR',true],
    58: ['BTC','EUR',true],
    59: ['ETH','EUR',true],
    60: ['BNB','EUR',true],
    61: ['BUSD','EUR',true],
    62: ['ADA','EUR',true],
    63: ['TRX','EUR',true],
    64: ['SHIB','EUR',true],
    65: ['MATIC','EUR',true],
    66: ['SOL','EUR',true],
    67: ['DAI','EUR',true],
    68: ['DOGE','EUR',true],
    69: ['DOT','EUR',true],
    70: ['USDT','TRY',true],
    71: ['BTC','TRY',true],
    72: ['ETH','TRY',true],
    73: ['BNB','TRY',true],
    74: ['BUSD','TRY',true],
    75: ['ADA','TRY',true],
    76: ['TRX','TRY',true],
    77: ['SHIB','TRY',true],
    78: ['MATIC','TRY',true],
    79: ['SOL','TRY',true],
    80: ['DAI','TRY',true],
    81: ['DOGE','TRY',true],
    82: ['DOT','TRY',true],
    83: ['DOT','TRY',true],
    84: ['DOT','TRY',true],
}
const ip: any = {}

Object.entries(pairs).map((v, k) => {
    ip[v[0]] = []
});

const fresh = (pArr: any) => {
    if (pArr.length > 1 && pArr[0].x < Date.now()-15*60*1000) {
        pArr.shift();
        fresh(pArr)
    }
}

export function App() {
    const [points, setPoints] = useState(ip)
    // let [searchParams, setSearchParams] = useSearchParams();

    const dsets: any = {'datasets': []}

    Object.entries(pairs).map((v, k) => {
        const [pid, [coin, cur, isSell]] = v;
        dsets.datasets.push({
            label: `${coin}/${cur} ${isSell?'Sell':'Buy'}`,
            data: points[pid],
            borderColor: isSell?'red':'blue',
        })
    });

    evtSource.onmessage = (event) => {
        const nd = JSON.parse(event.data)
        const pc = structuredClone(points)
        for (const k in pc) {
            if (nd[k]) { // at least 1 new point received
                if (pc[k].length > 1) { // old points exists in chart
                    if (pc[k].slice(-1).y == nd[k].y) { // the last point in chart == new received point
                        pc[k].pop() //todo: prev-prev point check
                    }
                    fresh(pc[k])
                }
                pc[k].push(nd[k])
            }
        }
        setPoints(pc)
        // console.log(pc)
    }

    useEffect(() => {
        console.log('.')
    }, [points]);

    return <div>
        <Scatter options={options} data={dsets}/>
    </div>;
}
