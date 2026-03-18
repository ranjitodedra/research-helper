This is the Related work section of thesis 
"
The adoption of electric vehicles (EVs) is a key strategy for reducing automobile emissions.
However, ensuring the viability of long-distance travel is essential for replacing conventional
transportation systems. In [14], the authors developed a tool to identify faster routes for
long-distance travel while minimizing charging times, particularly for highway journeys.
Hung et al. [15] proposed an optimization framework to determine optimal routing strate
gies for EVs across a network of charging stations. Their approach aimed to enhance
overall system performance by not only improving routing efficiency but also alleviating
traffic congestion near charging stations and reducing the load on the power grid.
Li et al. [26] constructed a dynamic road network model using graph theory and applied
Dijkstra’s shortest path algorithm for EV routing. This model supports efficient navigation
while accounting for the dynamic nature of road networks. Furthermore, Erdelic and
Caric [10] addressed the Electric Vehicle Routing Problem with Time Windows (EVRPTW)
in the context of goods delivery. Their solution incorporates both partial and full charging
strategies and is formulated as a Mixed Integer Linear Programming (MILP) problem to
optimize delivery schedules while managing energy constraints.
In [57], the authors aimed to plan a cost-efficient route from a depot to a destination
that meets customer requirements. Their primary objective was to minimize the total
cost associated with the trip. The numerical results showed that substantial cost savings
could be achieved by utilizing vehicles capable of partial recharging and energy recycling.
Similarly, the study in [18] addressed a charging routing problem in which smart EVs
identify suitable charging stations to fulfill their energy demands while minimizing expected
travel costs. The authors employed a Deep Reinforcement Learning (DRL) approach to
solve this routing problem effectively. In [24], a real-time charging scheduling model was
5
introduced for daily commuting, incorporating real-time traffic conditions. The model
differentiates between fast and slow charging stations and accounts for user preferences to
optimize both time and cost. Their proposed method demonstrated a potential reduction
in charging costs by an average of 45.9%. Lastly, Bautista et al. [5] tackled the problem
of charging station planning and slot booking. Their approach enables EVs to reserve
appropriate charging stations within a predefined time threshold, effectively contributing
to the minimization of total trip duration.
Several studies have employed Reinforcement Learning (RL) for managing EV charg
ing. For instance, in [2], the authors utilized RL along with historical data and statistical
analysis to evaluate the performance of their charging management strategy. In [32], the
authors proposed an efficient charging navigation model that accounts for uncertain traffic
conditions. They formulated the problem and introduced an improved Benders decompo
sition algorithm to solve it efficiently. Similarly, the work in [23] employed a model-free
Deep Reinforcement Learning (DRL) approach to optimize EV routing and charging sta
tion selection. Their results demonstrated improved performance in minimizing travel time,
waiting time, charging time, and driving distance compared to conventional approaches,
thereby offering an effective solution for EV navigation.
In contrast, Yan et al. [50] introduced a simulation framework that incorporates traf
f
ic and temperature variations to study EV load characteristics. Their findings revealed
significant seasonal and user preference-based variations in load billing, suggesting that
such detailed models can enhance renewable energy integration and support the scalability
of EV infrastructure. Alizadeh et al. [4] emphasized the importance of integrating trans
portation and power systems for effective EV routing and charging management. They
considered factors such as traffic conditions, road costs, dynamic electricity pricing, and
charging timing, and proposed an extended transportation graph model that incorporates
charging events for route optimization.
Energy consumption in EVs has also been studied extensively. Galvin [11] analyzed how
speed and acceleration affect energy consumption using regression-based models derived
from laboratory dynamometer tests on eight commercial EVs. The study showed that
even moderate acceleration can drastically increase energy consumption, adversely affecting
vehicle range and efficiency. Liu [31] focused on optimizing acceleration curves using genetic
algorithms to minimize energy consumption while maintaining driving comfort. Their
results indicated that a convex acceleration curve with β = 0.8 reduced energy consumption
by 2.23% compared to a linear profile.
Li et al. [27] investigated the impact of different acceleration profiles on battery degra
dation and energy usage. Their study highlighted the trade-off between minimizing energy
6
consumption and extending battery life. By modeling acceleration behaviors under var
ious driving conditions, neighborhood (0–40 km/h), urban (0–80 km/h), and highway
(0–120 km/h), they demonstrated that energy consumption per mile (ECPM) initially
decreases but then increases after reaching an optimal acceleration threshold.
In [30], the problem of effectively charging EVs is discussed, especially when there are
insufficient or no fixed charging stations (FCS). Movable charging stations (MCSs) are
suggested as a versatile solution to address this problem, dynamically shifting to satisfy
EV charging requests in real-time. This strategy lowers expenses, increases grid stability,
and makes charging more accessible, making it a viable option for EV networks in the
future. To reduce charging costs and lessen grid stress, EV charging scheduling must
be done optimally. Visakh et al. [45] suggested a scheduling technique based on convex
optimization that moves EV demand to off-peak hours, boosting load factor and voltage
stability while lowering peak demand by 41% and overall charging costs by 30.6%. Their
results demonstrate how real-time electricity pricing can improve system dependability
and economic efficiency. To optimize energy trading costs, Tushar et al. [44] offered an
EV classification scheme for photovoltaic-powered charging stations. This method divides
vehicles into three categories: premium, conservative, and green. Green EVs are used as
distributed storage. Using real solar and pricing data, they found that a mixed-integer
programming strategy greatly lowers operating costs when the percentage of green EVs
increases, especially during the winter.
Considering battery constraints and the availability of charging stations, Zhang et
al. [55] addressed the limitations of conventional vehicle routing models by formulating the
Electric Vehicle Routing Problem (EVRP) with charging stations. Their approach focuses
on minimizing energy consumption rather than distance, demonstrating that energy-aware
routing yields lower operational costs and a reduced environmental footprint. Similarly,
Yang et al. [52] proposed an Electric Vehicle Route Optimization Model that incorporates
Time-of-Use (TOU) electricity pricing to minimize distribution costs. By accounting for
battery capacity, charging duration, and vehicle load, and employing a Learnable Partheno
Genetic Algorithm (LPGA), their model effectively integrates expert knowledge to enhance
cost efficiency and improve grid reliability.
For Electric Vehicle Routing with Time Windows (E-VRPTW), Ham et al. [13] de
veloped a hybrid optimization framework that leverages TOU pricing to shift charging
activities to off-peak periods. Their mixed-integer programming and constraint program
ming (MIP-CP) hybrid approach outperforms traditional methods, achieving energy cost
savings of up to 15%. In a related direction, Zhong et al. [56] proposed an integrated
energy scheduling model involving EVs, residential energy systems, and workplace stor
age. By incorporating grid-to-vehicle (G2V) and vehicle-to-grid (V2G) technologies, their
7
approach enables smart charging and discharging strategies that reduce electricity costs
while enhancing grid stability and renewable energy usage.
Furthermore, Lin et al. [28] designed optimal online EV charging algorithms that op
erate using real-time electricity pricing without relying on future price forecasts. By ap
plying adaptive charging strategies, their model significantly lowers charging costs and
mitigates user inconvenience, outperforming conventional scheduling approaches in both
cost-effectiveness and grid efficiency.
Liu et al. [30] investigated the use of movable charging stations (MCSs) to address the
limitations of fixed charging infrastructure. Their approach improves accessibility and grid
stability by dynamically deploying charging stations based on demand. While innovative
from an infrastructure standpoint, this work does not address routing optimization or
real-time energy pricing.
Visakh et al. [45] proposed a convex optimization technique for EV charging that shifts
demand to off-peak hours, improving grid stability and reducing charging costs. Although
their scheduling method is effective for balancing electrical loads, it does not incorporate
vehicle routing decisions or battery constraints and assumes static vehicle behavior without
accounting for dynamic road conditions.
Tushar et al. [44] focused on minimizing charging station operational costs by classifying
EVs based on usage patterns in photovoltaic-powered stations. Their use of mixed-integer
programming to support energy trading strategies highlights the potential of smart charg
ing infrastructure. However, their model centers on energy economics at the station level
and does not address vehicle mobility or travel optimization.
Other researchers have tackled the Electric Vehicle Routing Problem (EVRP) more di
rectly. Zhang et al. [55] integrated battery limitations and recharging stations into routing
models, showing that energy-aware routing outperforms traditional distance-based meth
ods in terms of efficiency and cost. Similarly, Yang et al. [52] and Ham et al. [13] incorpo
rated Time-of-Use (TOU) electricity pricing into routing models to enhance cost efficiency,
using heuristic and hybrid optimization techniques. Although these studies advance the
f
ield by considering energy dynamics and pricing, they often assume static traffic condi
tions and overlook real-time responsiveness, an essential feature for large-scale, real-world
applications.
Beyond routing, studies such as Zhong et al. [56] have explored integrated energy
scheduling across home, work, and EV storage systems, focusing on grid-to-vehicle (G2V)
and vehicle-to-grid (V2G) interactions. While their model effectively reduces electricity
costs and promotes renewable energy utilization, it is primarily designed for stationary
energy systems and not mobile EV travel. Similarly, Lin et al. [28] proposed online EV
8
charging algorithms that adapt to real-time electricity pricing without relying on future
forecasts. Their approach improves cost and satisfaction from a scheduling perspective but
does not factor in traffic-aware routing or charging station location.
This thesis presents a comprehensive approach to addressing the challenges of EV rout
ing and charging by integrating real-time traffic dynamics and accurate energy consumption
modeling. As an EV progresses from its source to the destination, it may encounter unex
pected traffic conditions that necessitate dynamic route adjustments. Energy consumption
plays a pivotal role in this decision-making process, enabling the EV to assess whether de
tours or alternative paths are viable and to identify optimal charging stations along the
way. Building upon foundational concepts from prior research, this thesis offers a uni
f
ied solution that tackles EV routing, charging decisions, and real-time traffic disruptions.
The proposed methodology aims to minimize both total travel time and charging costs
by resolving the interconnected routing and charging optimization problems in a dynamic
environment.
" 
from my senior I want you to take the outline or structure of section. igonre the topic but take note of that structure and remember it. 
now this 
"
\section{Related Work}\label{related_work}

With the rise of electric vehicles, researchers began extending VRP to account for limited battery ranges and charging infrastructure. Erdoğan and Miller-Hooks (2012)~\cite{erdougan2012green} formulated a Green Vehicle Routing Problem (VRP) for alternative fuel fleets, highlighting the challenges of limited driving range and sparse charging station availability. They developed two tailored construction heuristics, the Modified Clarke-\&-Wright savings approach and a Density-Based Clustering Algorithm supplemented by a custom tour-improvement phase. Computational experiments showed these methods closed most optimality gaps and underscored how route feasibility depends on the spatial distribution of customers and refuelling sites. Subsequent early EVRP models introduced explicit route planning with battery constraints: for instance, Gendreau et al.~\cite{gendreau2015time} incorporate time-dependent road speeds into an EVRP with time windows. These studies established the core EVRP framework of incorporating energy consumption and charging stops into routing.  Later work began to couple routing with real-time network conditions, Lu et al.~\cite{lu2020time}  proposed a Time-Dependent EVRP whose travel times (and hence energy use) vary with traffic, allowing edge-cost updates as congestion evolves. These contributions established the core EVRP framework of incorporating energy consumption, charging stops, and time-varying travel speeds into routing.

\vspace{1em}

 % Routing Optimization in EV Logistics
 Another frontier in EV routing research is the integration of real-time data and dynamic decision-making. Recent models consider time-dependent travel speeds, traffic congestion, and time-varying energy consumption in the routing of EVs. For example, Zhao et al.~\cite{zhao2025electric} defined a time and load dependent EVRP (TLD-EVRP) that accounts for real-time traffic conditions and vehicle load effects on energy use. In such models, an EV’s energy consumption rate can change with payload and driving speed, and routes may need to adapt on the fly to traffic delays or updated charging station statuses. Researchers have begun employing techniques like dynamic programming, rolling horizon optimization, and even machine learning (e.g., reinforcement learning) to re-optimize EV routes as conditions evolve. Gendreau et al.~\cite{gendreau2015time} emphasized that dynamic vehicle routing problems involve a trade-off between quickly generating updated routes and ensuring those routes remain efficient. This challenge is particularly pronounced in electric vehicle routing, where considerations such as battery capacity and charging or swapping requirements further complicate timely decision-making. Accordingly, recent dynamic EVRP studies proposed real-time rerouting algorithms that ensure vehicles can reach charging options in time despite unforeseen delays, while minimizing total distance or energy cost. These contributions pave the way for more resilient and intelligent EV logistics systems that can handle stochastic traffic and energy variables.

 \vspace{1em}

 % Battery Swapping and Swapping Infrastructure
 Researchers soon explored battery swapping as an alternative to charging, aiming to reduce the lengthy recharging times. Yang \& Sun~\cite{yang_battery_2015} introduced the BSS–EV–LRP, alternating swap-station location with route construction under battery-range limits. In this paradigm, an EV with a low battery can quickly exchange it for a fully charged battery at a station, instead of waiting to recharge. By leveraging swap stations, these models effectively eliminate most of the dwell time for energy replenishment, thereby improving route throughput. Hof et al.~\cite{hof_solving_2017} extended this concept using an adaptive VNS that lowered the number of stations required but still assumed static travel time. Chen et al.~\cite{chen_solving_2021} later tackled a mixed fleet of electric and diesel trucks with a heuristic branch-and-price scheme, again optimising cost under fixed network conditions. These papers tighten infrastructure decisions but leave en-route replanning and granular battery operations unexplored. EVRP-BSS formulations highlight the trade-off between investing in swapping infrastructure and the operational savings from faster “refueling,” and they demonstrated that strategically placed swap stations can enable EV routes comparable to conventional vehicles in efficiency.

\vspace{1em}

Li et al.~\cite{li_electric_2020} built a BVRP-EC model that jointly minimises power use, carbon emissions, and travel time, solved by a GA-hill-climbing hybrid. Their energy model is rich, yet they considered swapping the entire battery pack and keeping the planned route fixed once the trip starts. Jie et al.~\cite{jie_two-echelon_2019} broadened the scope to a two-echelon EVRP with swap stations, improving urban efficiency but still using fixed road-travel times. Such studies highlight environmental trade-offs but ignore real-time traffic and partial-swap possibilities. Adler \& Mirchandani~\cite{adler_online_2014} balanced station inventory against vehicle delays via an online algorithm that reserves full batteries in advance, minimising expected travel time though without customer-delivery objectives. Ni et al.~\cite{ni_inventory_2021} combined long-term battery inventory planning with real-time vehicle-to-station routing to maximise BSS-network revenue. Both works embrace on-the-fly decision-making, but neither replans the customer sequence after each stop, nor handles vehicle load limits ~\cite{adler_online_2014}.  Raeesi \& Zografos~\cite{raeesi_coordinated_2022} synchronised mobile swapping vans with delivery EVs, underscoring the value of intra-route refuelling yet still treating swaps as full-pack replacements and holding customer order constant.

\vspace{1em}

% Segment-Level Battery Swapping and Granular Swap Strategies
Most EVRP literature assumes a full-battery swap or full recharge at each station. A few studies have begun to relax this: Keskin and Çatay~\cite{keskin2016partial} proposed an EVRPTW variant allowing partial recharging (up to 80\% charge) rather than always full charge. Their experiments show that such granular recharge policies can significantly improve routing decisions. To our knowledge, equivalent “segment-level” or partial battery swapping (replacing only some battery modules) is not explicitly modeled in EVRP. This suggests an open area: while partial recharge policies exist, analogous partial-swap or modular-swap strategies have not been studied in the routing literature.

\vspace{1em}

% Mixed-Integer Programming and Exact Methods for EVRP-BSS
Several works formulated EVRP-BSS problems as Mixed-Integer Programs. Yang and Sun~\cite{yang_battery_2015} provided a MILP for the BSS–EV–LRP (swap station siting plus routing). 

Desaulniers et al.~\cite{lam2022branch} used branch-price-and-cut for EVRPTW, and others applied branch-and-bound to small EVRP instances. 
 
for instance, Yang and Sun~\cite{yang_battery_2015} compared CPLEX solutions on small instances. The high combinatorial complexity (especially when adding station location or time-dependent elements) often necessitates advanced techniques like branch-and-price, cut generation, or time-expansion models to achieve exact solutions.

\vspace{1em}

% Heuristic and Metaheuristic Approaches for Battery Swapping EVRP
Due to the problem size, most EVRP-BSS studies rely on heuristics. Yang and Sun~\cite{yang_battery_2015} developed a multi-phase adaptive large neighborhood search (ALNS) hybrid called SIGALNS: it alternates between locating BSSs and routing EVs, with tabu-search intensification. Zhang et al.~\cite{li2025battery}  likewise used an improved ALNS with custom operators to solve the moped-delivery BSSLRP. Genetic algorithms, simulated annealing, ant colony, and other metaheuristics have also been applied. For example, Tanguy et al.~\cite{longhitano2024joint} embedded battery SoH estimation into an EVRP and solved it via a tailored GA. In sum, solution approaches frequently combined VRP search techniques (sweep, savings, neighborhood search) with problem-specific operators for swapping; these metaheuristics generated high-quality routes and station plans for large instances.

\vspace{1em}

% Reinforcement Learning and AI-Based Routing for EV Systems

Recent works explored AI for EV routing. Sayarshad et al.\cite{sayarshad2021intelligent} implemented a look-ahead MDP for dynamic EV taxi routing with swapping stations, and optimized fleet assignments and pricing via an MDP policy. Safe Reinforcement Learning was used for stochastic EVRP: Basso et al.\cite{basso2022dynamic} formulated a Dynamic Stochastic EVRP and proposed a Safe RL policy to minimize expected energy use while avoiding battery depletion. Choudhury et al.~\cite{narayanan2022reinforcement} presented “QuikRouteFinder,” a value-based RL agent for an EVRP that included vehicle-to-grid discharge; their agent learned offline to enable fast routing decisions at scale. Collectively, these studies showed that RL/AI could address EVRP variants in which explicit modeling was difficult (e.g., stochastic demand and multi-service settings), although such approaches remained relatively nascent in the literature.

\vspace{1em}

In conclusion to the above streams, we address an EVRP-BSS whose primary objective is the minimization of total delivery time under dynamic conditions. The proposed framework optimized the route at every visited node using live traffic data. Furthermore, none of the cited studies considered swapping only depleted battery modules to reduce downtime. We proposed a framework that incorporated load-aware energy consumption to reduce energy cost. By integrating these components into a unified optimization framework, we filled this gap and accelerated electric delivery operations. 

"
is latex code to of Related work section from paper 1 and this is 
"
\section{Related Work}\label{related_work}

The Electric Vehicle Routing Problem (EVRP) extends the classical VRP by incorporating state-of-charge (SoC) constraints and charging-station stops, while separate strands of the literature evaluate infrastructure choices and their impacts on the power grid and traffic. More recently, studies have also begun coupling routing with DWC and with time-dependent traffic models. Below we synthesize these threads and identify the concrete modelling gaps relevant to last-mile delivery.

% EV Routing and Energy-Aware Modelling
Because battery capacity directly constrains route feasibility, energy-aware formulations lie at the heart of the EVRP. \citet{erdogan_green_2012} introduced modified Clarke-\&-Wright savings and density-based clustering heuristics for the G-VRP, demonstrating that feasibility hinges on the spatial configuration of dropping location and refuelling sites. Subsequent models enriched the energy dimension: \citet{gutierrez-alcoba_stochastic_2023} formulated the Stochastic Inventory Routing Problem on Electric Roads (S-IRP-ER), employing isochrone graphs that track battery SoC continuously as a hybrid vehicle charges and discharges along electrified arcs, and solved the problem with a mathematical-programming heuristic validated on realistic instances. In a comprehensive review of 140 studies, \citet{wang_review_2025} contrasted static-charging and dynamic-charging EVRP paradigms, observing that classical heuristic and metaheuristic algorithms are well developed for stationary-charging variants but remain poorly adapted to dynamic-charging settings, and that deep reinforcement learning approaches, while promising, are under-explored at scale. A common limitation across these formulations is the treatment of energy consumption as a fixed per-kilometre rate: none of the above models captures the payload-dependent drain that arises in last-mile delivery, where battery draw decreases progressively as parcels are offloaded. This omission can lead to suboptimal route sequences when vehicles start heavily loaded.

% Stationary Charging and Battery Swapping

Stationary charging infrastructure fast chargers and battery-swapping stations (BSS) introduces detour and dwell-time costs that directly affect total delivery time. \citet{chen_optimal_2016} developed a user-equilibrium model for networks with dedicated charging lanes and optimised their deployment via a mathematical program with complementarity constraints, while \citet{chen_deployment_2017} extended this line to compare charging lanes and fixed stations along traffic corridors under both public and private provision, finding that charging lanes are competitive in revenue generation. From a multi-modal perspective, \citet{borjesson_stationary_2025} built a multi-day truck-trip cost model comparing stationary charging, catenary electric roads, and battery swapping in the EU TEN-T network, showing that swapping and catenary systems can reach cost parity by 2035 while outperforming stationary charging. \citet{aldhanhani_future_2024} surveyed emerging Vehicle-to-Everything paradigms and fast-charging station routing for EVs, underscoring coordinated demand management as essential to prevent grid overload.

% Dynamic Charging, ERS, and DWC

ERS, encompassing inductive, conductive, and catenary technologies, enable vehicles to replenish energy while in motion, fundamentally altering routing energy tradeoffs. \citet{chen_electrification_2015} provided an early technology survey of eRoad concepts and identified key integration gaps for Inductive Power Transfer within road infrastructure. \citet{amjad_wireless_2022} later offered a comprehensive review of wireless charging methods, covering capacitive and inductive transfer, stationary and dynamic variants, control systems, and battery considerations. On the deployment side, \citet{fuller_wireless_2016} showed that a 40\,kW DWC system covering inter-city routes in California is more cost-effective over a ten-year horizon than gasoline refuelling, even at low battery prices, while \citet{mubarak_strategic_2021} formulated a network design problem for in-motion wireless CS that explicitly targets range-anxiety alleviation.

Several studies address the interaction between DWC lane placement and traffic dynamics. \citet{tran_dynamic_2022} embedded a multi-class dynamic system-optimal traffic model into a mixed-integer linear program for charging-lane siting, capturing congestion effects across vehicle classes. \citet{liu_optimal_2021} jointly optimised DWC link locations and electricity prices to minimise social cost under stochastic user equilibrium. \citet{he_optimal_2020} highlighted that wireless charging lanes can reduce effective road capacity, a factor ignored in earlier models. At the component level, \citet{karlsson_energy_2021} demonstrated that charger topology strongly influences on-road energy consumption and battery ageing for buses on conductive electric roads, and \citet{lewis_optimal_2023} showed that speed-compensated power sharing can cut average power demand by 21\% while increasing simultaneous vehicle-hosting capacity by 30\%. \citet{majhi_assessment_2022} developed a traffic-simulation framework for Auckland's motorway ERS, quantifying minimum DWC facility length and spatio-temporal energy demand, and \citet{li_economic_2023} evaluated DWC economic viability for private EVs with renewable-energy integration, finding that dynamic pricing shortens the payback period by 25\%. Although these works illuminate where and how to deploy DWC, they operate at the infrastructure or aggregate-flow level and do not model individual vehicle routing decisions, payload-dependent energy draw.

% Joint Routing and Charging Scheduling Algorithms

A literature integrates routing decisions with charging or DWC. \citet{cao_joint_2023} formulated a joint routing and wireless charging scheduling problem for IoT-enabled EVs operating shuttle services, minimising travel distance, charging cost, and battery degradation via a customised Benders decomposition; an improved variant exploiting trajectory similarity reduced computation time by over 50\%. \citet{tran_dynamic_2022} coupled dynamic traffic assignment with charging-lane location in a bi-level framework, though routing remains at the aggregate origin--destination level rather than per-vehicle sequencing. \citet{wang_enabling_2024} proposed a Deep Slack Induction by String Removals-based Reinforcement Learning (DSRL) framework for shared autonomous vehicles under DWC, optimising cost efficiency and SoC stabilisation; experiments showed superior performance over heuristic baselines with robust generalisation across instance sizes and power levels. Common to all three approaches, however, are simplifying assumptions that limit their applicability to last-mile delivery: shuttle or SAV settings with homogeneous loads, fixed or simplified energy models. None considers a delivery truck whose payload (and hence energy consumption rate) decreases at each successive dropping location stop.

% Cost, Feasibility, and Institutional Barriers                    

The viability of any ERS- or BSS-integrated routing system ultimately depends on techno-economic and institutional factors. \citet{deshpande_breakeven_2023} established that ERS can reduce well-to-wheel emissions by approximately 10\% and electrify up to 72\% of a country's road freight within a 20-year breakeven horizon, while \citet{li_economic_2023} showed that DWC profitability is highly sensitive to charging efficiency and dynamic pricing policy. At the vehicle-operation level, \citet{borjesson_stationary_2025} found that battery swapping and catenary ERS reach cost parity for multi-day trucking by 2035, underscoring the operational relevance of swap-based strategies. Yet \citet{scherrer_institutional_2026}, drawing on 22 expert interviews across eight European countries, revealed that ERS deployment faces deep institutional barriers conflicts between government commitment requirements and technology-neutral policy stances, time pressures favouring readily available stationary solutions, and cross-border coordination challenges. \citet{alanazi_potential_2025} corroborated these findings through a comparative survey of Gulf Cooperation Council (GCC) and Nordic regions, highlighting divergent infrastructure readiness levels. These studies confirm that both DWC and BSS pathways are economically plausible but institutionally contingent, motivating operational models that can flexibly exploit whichever charging modalities are available in a given network.

% Synthesis and Open Gaps                    

The literature reviewed above advances EV routing, charging deployment, and DWC technology along largely separate tracks. Energy-aware EVRP formulations~\citep{erdogan_green_2012, gutierrez-alcoba_stochastic_2023, wang_review_2025} capture SoC dynamics but assume constant per-kilometre energy rates, ignoring the progressive payload reduction inherent in delivery operations. Battery-swapping and stationary-charging studies~\citep{chen_optimal_2016, chen_deployment_2017, borjesson_stationary_2025, aldhanhani_future_2024} treat charging as a stationary operation and do not integrate DWC or electrified road segments into their routing frameworks. The extensive DWC/ERS literature~\citep{chen_electrification_2015, fuller_wireless_2016, majhi_assessment_2022, tran_dynamic_2022, liu_optimal_2021, amjad_wireless_2022, karlsson_energy_2021, lewis_optimal_2023, mubarak_strategic_2021, li_economic_2023, deshpande_breakeven_2023} focuses on infrastructure siting, power-system design, and aggregate traffic flows, without descending to per-vehicle route sequencing. Joint routing-and-charging algorithms~\citep{cao_joint_2023, wang_enabling_2024} target SAV or shuttle settings with homogeneous loads. Finally, no existing work jointly incorporates time-varying arc travel times, payload-dependent energy consumption, and the coexistence of stationary charging and DWC within a single per-vehicle routing optimisation framework. 
"
introduction section's latex code of my paper 2 I want you to write thesis Related work section for MY THESIS using to the Related work section of my both papers. the output section also should be latex code. Use references and keep it same as it is given in the latex code of the papers. Maintain the academic tone. YOU dont even need to paraphrase anything from related work section of paper just maintain the flow. (Note Please don't not paraphase anything if not needed)