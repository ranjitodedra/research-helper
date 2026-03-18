This is table that summries the related work section of my paper 1
"
Table~\ref{tab:relwork-summary} provided a concise summary of each research paper discussed in this section, outlining the problem studied, the approach taken, and key limitations.

\begin{table*}[!tbp]
  % \centering
  \caption{Summary of related work on EV routing and battery swapping}
  \label{tab:relwork-summary}
  \renewcommand{\arraystretch}{1.1}
  \resizebox{\textwidth}{!}{%
  \begin{tabular}{p{2.5cm} p{3cm} p{4cm} p{3cm}}
    \toprule
    \textbf{Author (Year)} &
    \textbf{Problem Studied} &
    \textbf{Approach / Solution} &
    \textbf{Key Limitations} \\
    \midrule
    Erdoğan \& Miller\hyp Hooks (2012)~\cite{erdougan2012green} &
    Green VRP for alt-fuel fleets &
    MILP \& heuristics (C\&W, clustering) &
    Static travel times, no rerouting \\[2pt]

    Gendreau \textit{et al.} (2015)~\cite{gendreau2015time} &
    EVRP with time windows &
    Time-dependent speeds in the routing model &
    Off-line planning, no live updates \\[2pt]

    %  - NEW  -
    Keskin \& Çatay (2016))~\cite{keskin2016partial} &
    E-VRPTW with \textbf{partial recharging} &
    MILP \& Adaptive LNS permitting <100 \% charges &
    No swapping, static network, modest instance size \\[2pt]

    Desaulniers \textit{et al.} (2016)~\cite{lam2022branch} &
    E-VRPTW (multiple recharges) &
    Branch-price-and-cut exact method &
    Exact but limited to small/medium instances \\[2pt]
    %      

    Lu \textit{et al.} (2020)~\cite{lu2020time} &
    Time-Dependent EVRP &
    ILP \& Iterated VNS with speed optimisation &
    Medium instances only, full recharge, deterministic \\[2pt]

    Zhao \textit{et al.} (2020)~\cite{zhao2025electric} &
    Time \& load dependent EVRP &
    Dynamic edge costs via live congestion data &
    Fixed customer order, full-pack charging \\[2pt]

    %  - NEW  -
    Sayarshad \textit{et al.} (2020)~\cite{sayarshad2021intelligent} &
    Dynamic EV taxi routing with swapping &
    Look-ahead MDP / RL fleet assignment &
    No partial swap, ignores payload effects \\[2pt]
    %      

    Yang \& Sun (2021)~\cite{yang_battery_2015}  &
    BSS–EV–LRP (location \& routing) &
    Alternating station siting and routing (ALNS) &
    Static network, no en-route replanning \\[2pt]

    Hof \textit{et al.} (2021)~\cite{hof_solving_2017} &
    EVRP with battery swapping &
    Adaptive VNS minimising station count &
    Assumes fixed travel times \\[2pt]

    Chen \textit{et al.} (2022)~\cite{chen_solving_2021} &
    Mixed diesel/EV fleet with BSS &
    Heuristic branch-and-price &
    Static conditions, single-stage plan \\[2pt]

    Li \textit{et al.} (2022)~\cite{li_electric_2020} &
    BVRP-EC (energy, carbon, time) &
    GA \& hill-climbing hybrid &
    Route fixed after start, full-pack swap \\[2pt]

    %  - NEW  -
    Basso \textit{et al.} (2022)~\cite{basso2022dynamic} &
    Dynamic stochastic EVRP &
    Safe RL policy to avoid depletion &
    Full recharge only, small testbed \\[2pt]

    Choudhury \textit{et al.} (2022)~\cite{narayanan2022reinforcement} &
    EVRP with V2G discharge (QuikRouteFinder) &
    Value-based RL (offline learning) &
    No fleet coordination, static station set \\[2pt]
    %      

    Jie \textit{et al.} (2023)~\cite{jie_two-echelon_2019} &
    Two-echelon EVRP with swaps &
    Urban-delivery heuristic &
    Ignores real-time traffic, full-pack swap \\[2pt]

    Adler \& Mirchandani (2023)~\cite{adler_online_2014} &
    Online battery reservation &
    Competitive online algorithm &
    No customer-delivery optimisation, static routing \\[2pt]

    %  - NEW  -
    Tanguy \textit{et al.} (2023)~\cite{longhitano2024joint} &
    EVRP with battery degradation (SoH) &
    Genetic algorithm with SoH cost in the objective &
    Full charges, no dynamic traffic \\[2pt]
    %      

    Ni \textit{et al.} (2024)~\cite{ni_inventory_2021} &
    BSS inventory \& real-time dispatch &
    Revenue-maximising model &
    No customer resequencing, ignores load \\[2pt]

    Raeesi \& Zografos (2024)~\cite{raeesi_coordinated_2022} &
    Mobile swap vans synchronised with EVs &
    On-route swap-van scheduling &
    Customer order fixed, full-pack swap \\[2pt]

    Zhang \textit{et al.} (2025)~\cite{li2025battery} &
    BSS location-routing for e-moped fleet &
    Improved ALNS with custom destroy–repair moves &
    Static demand, full-pack swap, mid-size instances \\[2pt]
    %      

    \bottomrule
  
  \end{tabular}
  }
\end{table*}
"
I want you to create table like this for related work of my paper 2, here is latex code
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




In this thesis, we focus on a real-time traffic-aware road network. 

To build this scenario, we utilize SUMO as our traffic simulator, which allows for microscopic traffic modeling. 

The road network data is collected using OpenStreetMap (OSM), and we extract specific regions of interest (from London, Canada, to Fredericton, Canada) through Overpass Turbo, which provides a flexible interface for querying OSM data. 

By integrating SUMO with these real world map sources, we are able to simulate dynamic road conditions, including varying traffic densities and travel times. This setup enables us to evaluate our electric vehicle
routing and charging strategies under time-sensitive traffic scenarios.

Additionally, we utilize traffic multipliers to dynamically update traffic conditions, enabling our model to more accurately reflect real-world scenarios. This approach helps simulate traffic fluctuations and enhances the accuracy of route planning and charging decisions.