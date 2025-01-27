# Remise

Ajuste le document "plan-v1.md" de façon à respecter ces consignes :

Consigne 0: 
Rédiger le document en LaTeX.

Consigne 1:
Le document doit contenir ces sections :

- Description du problème
- Revue de littérature
- Choix du modèle LLM
- Choix de l'approche
- Données utilisées
- Évaluation du système
- Tâches à faire
- Bibliographie


Consigne 2:
La revue de littérature doit discuter de 5 à 10 articles 
pertinents à notre problème à résoudre et qui nous aident à orienter notre recherche.
Mettre les références de ces articles dans la bibliographie à la fin du document.

Consigne 3:
Pour le choix du modèle, je dois identifier au moins 2 modèles de langage naturel qui pourraient être utilisés pour résoudre le problème.
Some models (e.g. Llama 3.1/3.2, Mistral, Qwen and more) were trained to use tools.
Expliquer pourquoi et comment certains modèles pourraient être plus adaptés que d'autres pour résoudre le problème.
J'ai pensé à mistral-7b.
Est-ce que deepseek-7b pourrait être un bon choix?
est-ce que qwen-7b pourrait être un bon choix?
Trouver les articles ou des références qui dit que ces modèles ont été entrainés à utiliser des outils.

Consigne 4:
Pour le choix de l'approche, je dois identifier au moins 2 approches qui pourraient être utilisées pour résoudre le problème.
Les deux approches sont RAG et Agents. 
Expliquer ces approches et les comparer.
Expliquer le pipeline pour l'approche choisie.

Consigne 5:
Pour les données utilisées, expliquer les données d'Open Food Facts.
Décrire le jeu de données. Donner des statistiques sur le nombre de données, le nombre de colonnes, le nombre de lignes, etc.
Les attributs, des données manquantes. Montréer des exemples pour illustrer cela.

Consigne 6:
Pour la section évaluation du système, je dois expliquer comment je vais évaluer le système.
Il faut identifier des métriques de performance pour évaluer le système, notamment la qualité des réponses et la rapidité.
Identifier au moins 3 métriques.

Consigne 7:
Pour la section tâches à faire, il faut identifier les tâches à faire pour compléter le projet.
On doit cumuler 270 heures de travail, y compris la rédaction du présent rapport et la préparation de la présentation orale.

Consigne 8:
Dans la section bibliographie, il faut mettre les références des articles cités dans la revue de littérature.

Voici les articles que j'ai choisis pour la revue de littérature : 

@article{schulhoff2024prompt,
  title={The Prompt Report: A Systematic Survey of Prompting Techniques},
  author={Schulhoff, Sander and Ilie, Michael and Balepur, Nishant and Kahadze, Konstantine and Liu, Amanda and Si, Chenglei and Li, Yinheng and Gupta, Aayush and Han, HyoJung and Schulhoff, Sevien and others},
  journal={arXiv preprint arXiv:2406.06608},
  year={2024}
}

@article{huang2024survey,
  title={A Survey on Retrieval-Augmented Text Generation for Large Language Models},
  author={Huang, Yizheng and Huang, Jimmy},
  journal={arXiv preprint arXiv:2404.10981},
  year={2024}
}

@article{wang2024survey,
  title={A survey on large language model based autonomous agents},
  author={Wang, Lei and Ma, Chen and Feng, Xueyang and Zhang, Zeyu and Yang, Hao and Zhang, Jingsen and Chen, Zhiyuan and Tang, Jiakai and Chen, Xu and Lin, Yankai and others},
  journal={Frontiers of Computer Science},
  volume={18},
  number={6},
  pages={186345},
  year={2024},
  publisher={Springer}
}

Cet article est également disponible ici :
A Survey on Large Language Model based Autonomous Agents
https://arxiv.org/pdf/2308.11432

@article{xi2023rise,
  title={The rise and potential of large language model based agents: A survey},
  author={Xi, Zhiheng and Chen, Wenxiang and Guo, Xin and He, Wei and Ding, Yiwen and Hong, Boyang and Zhang, Ming and Wang, Junzhe and Jin, Senjie and Zhou, Enyu and others},
  journal={arXiv preprint arXiv:2309.07864},
  year={2023}
}

@article{hong2024next,
  title={Next-Generation Database Interfaces: A Survey of LLM-based Text-to-SQL},
  author={Hong, Zijin and Yuan, Zheng and Zhang, Qinggang and Chen, Hao and Dong, Junnan and Huang, Feiran and Huang, Xiao},
  journal={arXiv preprint arXiv:2406.08426},
  year={2024}
}

@article{mohammadjafari2024natural,
  title={From Natural Language to SQL: Review of LLM-based Text-to-SQL Systems},
  author={Mohammadjafari, Ali and Maida, Anthony S and Gottumukkala, Raju},
  journal={arXiv preprint arXiv:2410.01066},
  year={2024}
}

@article{li2024can,
  title={Can llm already serve as a database interface? a big bench for large-scale database grounded text-to-sqls},
  author={Li, Jinyang and Hui, Binyuan and Qu, Ge and Yang, Jiaxi and Li, Binhua and Li, Bowen and Wang, Bailin and Qin, Bowen and Geng, Ruiying and Huo, Nan and others},
  journal={Advances in Neural Information Processing Systems},
  volume={36},
  year={2024}
}

@article{song2024speech,
  title={Speech-to-SQL: toward speech-driven SQL query generation from natural language question},
  author={Song, Yuanfeng and Wong, Raymond Chi-Wing and Zhao, Xuefang},
  journal={The VLDB Journal},
  pages={1--23},
  year={2024},
  publisher={Springer}
}

@article{biswal2024text2sql,
  title={Text2sql is not enough: Unifying ai and databases with tag},
  author={Biswal, Asim and Patel, Liana and Jha, Siddarth and Kamsetty, Amog and Liu, Shu and Gonzalez, Joseph E and Guestrin, Carlos and Zaharia, Matei},
  journal={arXiv preprint arXiv:2408.14717},
  year={2024}
}


@article{yang2024synthesizing,
  title={Synthesizing text-to-sql data from weak and strong llms},
  author={Yang, Jiaxi and Hui, Binyuan and Yang, Min and Yang, Jian and Lin, Junyang and Zhou, Chang},
  journal={arXiv preprint arXiv:2408.03256},
  year={2024}
}


@article{liu2023agentbench,
  title={Agentbench: Evaluating llms as agents},
  author={Liu, Xiao and Yu, Hao and Zhang, Hanchen and Xu, Yifan and Lei, Xuanyu and Lai, Hanyu and Gu, Yu and Ding, Hangliang and Men, Kaiwen and Yang, Kejuan and others},
  journal={arXiv preprint arXiv:2308.03688},
  year={2023}
}

Voir aussi https://github.com/THUDM/AgentBench et https://llmbench.ai/agent

@article{zhang2024evaluation,
  title={Evaluation Agent: Efficient and Promptable Evaluation Framework for Visual Generative Models},
  author={Zhang, Fan and Tian, Shulin and Huang, Ziqi and Qiao, Yu and Liu, Ziwei},
  journal={arXiv preprint arXiv:2412.09645},
  year={2024}
}

@article{qiao2024benchmarking,
  title={Benchmarking Agentic Workflow Generation},
  author={Qiao, Shuofei and Fang, Runnan and Qiu, Zhisong and Wang, Xiaobin and Zhang, Ningyu and Jiang, Yong and Xie, Pengjun and Huang, Fei and Chen, Huajun},
  journal={arXiv preprint arXiv:2410.07869},
  year={2024}
}

Consigne 9:
Le document "plan-v1.md" n'a pas toutes les informations pertinentes.
Indique en rouge dans le document LaTeX des indications pour les parties à compléter.





