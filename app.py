def display_planet_interpretations(chart_data, interpretation_type):
    """Afișează interpretări specifice pentru toate planetele"""
    
    # INTERPRETĂRI NATALE COMPLETE PENTRU TOATE PLANETELE
    natal_interpretations = {
        "Sun": {
            "ARI": "Energetic, pioneering, courageous. Natural leader with strong initiative. Impulsive and direct in approach.",
            "TAU": "Practical, reliable, patient. Values security and comfort. Determined and persistent.",
            "GEM": "Clever, bright, quickwitted, communicative, able to do many different things at once, eager to learn new subjects. Openminded, adaptable, curious, restless, confident, seldom settling down.",
            "CAN": "Nurturing, emotional, protective. Strong connection to home and family. Sensitive and caring.",
            "LEO": "Confident, creative, generous. Natural performer and leader. Dramatic and warm-hearted.",
            "VIR": "Analytical, practical, helpful. Attention to detail and service-oriented. Methodical and precise.",
            "LIB": "Friendly, cordial, artistic, kind, considerate, loyal, alert, sociable, moderate, balanced in views, open-minded.",
            "SCO": "Intense, passionate, transformative. Deep emotional understanding. Powerful and determined.",
            "SAG": "Adventurous, philosophical, optimistic. Seeks truth and expansion. Freedom-loving and honest.",
            "CAP": "Ambitious, disciplined, responsible. Builds lasting structures. Serious and determined.",
            "AQU": "Innovative, independent, humanitarian. Forward-thinking and original. Unconventional and idealistic.",
            "PIS": "Compassionate, intuitive, artistic. Connected to spiritual realms. Dreamy and empathetic."
        },
        "Moon": {
            "ARI": "Energetic, ambitious, strongwilled, self-centred, impulsive, dominant & obstinate.",
            "TAU": "Steady, patient, determined. Values comfort and security. Emotionally stable.",
            "GEM": "Changeable, adaptable, curious. Needs mental stimulation. Restless emotions.",
            "CAN": "Nurturing, sensitive, protective. Strong emotional connections. Home-oriented.",
            "LEO": "Proud, dramatic, generous. Needs recognition and appreciation. Warm emotions.",
            "VIR": "Practical, analytical, helpful. Attention to emotional details. Service-oriented.",
            "LIB": "Harmonious, diplomatic, social. Seeks emotional balance. Relationship-focused.",
            "SCO": "Intense, passionate, secretive. Deep emotional currents. Transformative.",
            "SAG": "Adventurous, optimistic, freedom-loving. Needs emotional expansion. Philosophical.",
            "CAP": "Responsible, disciplined, reserved. Controls emotions carefully. Ambitious.",
            "AQU": "Independent, unconventional, detached. Unique emotional expression. Progressive.",
            "PIS": "Compassionate, intuitive, dreamy. Sensitive emotional nature. Spiritual."
        },
        "Mercury": {
            "ARI": "Quick-thinking, direct, innovative. Expresses ideas boldly and spontaneously.",
            "TAU": "Practical, methodical, persistent. Thinks carefully before speaking.",
            "GEM": "Versatile, communicative, curious. Learns quickly and shares knowledge.",
            "CAN": "Intuitive, emotional, memory-oriented. Thinks with heart and nostalgia.",
            "LEO": "Confident, dramatic, creative. Expresses ideas with flair and authority.",
            "VIR": "Analytical, precise, detail-oriented. Excellent at critical thinking.",
            "LIB": "Diplomatic, balanced, artistic. Seeks harmony in communication.",
            "SCO": "Penetrating, investigative, profound. Seeks hidden truths.",
            "SAG": "Philosophical, broad-minded, honest. Thinks in big pictures.",
            "CAP": "Practical, organized, ambitious. Strategic and disciplined thinking.",
            "AQU": "Innovative, original, detached. Thinks outside conventional boxes.",
            "PIS": "Intuitive, imaginative, compassionate. Thinks with psychic sensitivity."
        },
        "Venus": {
            "ARI": "Direct, passionate, impulsive in love. Attracted to challenge and excitement.",
            "TAU": "Sensual, loyal, comfort-seeking. Values stability and physical pleasure.",
            "GEM": "Social, flirtatious, communicative. Needs mental connection in relationships.",
            "CAN": "Nurturing, protective, home-oriented. Seeks emotional security.",
            "LEO": "Dramatic, generous, proud. Loves romance and admiration.",
            "VIR": "Practical, helpful, discerning. Shows love through service.",
            "LIB": "Harmonious, diplomatic, artistic. Seeks balance and partnership.",
            "SCO": "Intense, passionate, possessive. Seeks deep emotional bonds.",
            "SAG": "Adventurous, freedom-loving, honest. Values independence in relationships.",
            "CAP": "Serious, responsible, ambitious. Seeks stability and commitment.",
            "AQU": "Unconventional, friendly, detached. Values friendship and independence.",
            "PIS": "Romantic, compassionate, dreamy. Seeks spiritual connection."
        },
        "Mars": {
            "ARI": "Energetic, competitive, pioneering. Direct and assertive action.",
            "TAU": "Persistent, determined, practical. Slow but steady approach.",
            "GEM": "Versatile, quick, communicative. Action through words and ideas.",
            "CAN": "Protective, emotional, defensive. Actions driven by feelings.",
            "LEO": "Confident, dramatic, creative. Actions with flair and leadership.",
            "VIR": "Precise, analytical, efficient. Methodical and careful action.",
            "LIB": "Diplomatic, balanced, cooperative. Seeks harmony in action.",
            "SCO": "Intense, determined, transformative. Powerful and secretive action.",
            "SAG": "Adventurous, optimistic, freedom-loving. Action with purpose.",
            "CAP": "Ambitious, disciplined, patient. Strategic and persistent action.",
            "AQU": "Innovative, rebellious, independent. Unconventional action.",
            "PIS": "Compassionate, intuitive, adaptable. Action through inspiration."
        }
    }

    # INTERPRETĂRI SEXUALE COMPLETE
    sexual_interpretations = {
        "Sun": {
            "ARI": "Quick response, instant turn-on or turn-off. Won't pull punch. Can reach peaks quickly. Capable of multiple orgasms, but impatient with long foreplay. Once aroused, wants to get down to business. Super intense, but burns out quickly.",
            "TAU": "Sensual and patient lover. Enjoys prolonged foreplay and physical touch. Very tactile, appreciates comfort and luxury in sexual settings. Slow to arousal but deeply passionate once engaged.",
            "GEM": "Active, likes variety. Can try out any new technique, but gets bored easily. Sex is more fun & communication than hot passion. Sex is more mental than physical. Good at fantasy games, manual and oral techniques.",
            "CAN": "Nurturing and emotional lover. Sex is deeply connected to feelings and security. Needs emotional bond for best sexual experience. Very protective of partner.",
            "LEO": "Dramatic and generous lover. Enjoys being the center of attention in bed. Warm-hearted and passionate. Needs admiration and appreciation.",
            "VIR": "Attentive and perfectionist lover. Very concerned with technique and partner's satisfaction. May be overly critical or anxious about performance.",
            "LIB": "Seeks change in sex, not for variety but for its own sake. Will rarely beat around the bush; insists partner deliver the goods. Can play all sides of a menage-a-trois well.",
            "SCO": "Intense and transformative lover. Deeply passionate and investigative about sexuality. Powerful sexual energy that can be overwhelming.",
            "SAG": "Adventurous and experimental lover. Views sex as another form of exploration and learning. Enjoys variety and new experiences.",
            "CAP": "Serious and disciplined lover. Approaches sex with responsibility and control. May be reserved but deeply committed.",
            "AQU": "Innovative and unconventional lover. Enjoys experimenting with new ideas and techniques. Values friendship in sexual relationships.",
            "PIS": "Romantic and intuitive lover. Very sensitive to partner's needs and energy. Spiritual approach to sexuality."
        },
        "Moon": {
            "ARI": "Quick emotional responses in intimacy. Needs constant new stimulation. Impatient with slow pace. Emotionally demanding in relationships.",
            "TAU": "Steady emotional needs. Requires physical comfort and security. Very loyal and possessive in intimate relationships.",
            "GEM": "Curious and communicative about emotions. Needs mental connection for emotional satisfaction. Restless emotional nature.",
            "CAN": "Deeply nurturing and protective. Strong emotional bonds are essential. Very sensitive to partner's emotional state.",
            "LEO": "Dramatic emotional expression. Needs admiration and recognition. Warm and generous with emotions.",
            "VIR": "Analytical about emotions. Service-oriented in expressing care. May worry excessively about relationships.",
            "LIB": "Seeks emotional harmony and balance. Very diplomatic in expressing feelings. Needs partnership for emotional fulfillment.",
            "SCO": "Intense emotional depth. Transformative emotional experiences. Very private about true feelings.",
            "SAG": "Optimistic and freedom-loving emotionally. Needs space for emotional expression. Philosophical about relationships.",
            "CAP": "Reserved emotional expression. Disciplined approach to feelings. Serious about emotional commitments.",
            "AQU": "Unconventional emotional needs. Values friendship in emotional connections. Detached emotional style.",
            "PIS": "Compassionate and empathetic. Very sensitive emotionally. Spiritual emotional connections."
        },
        "Venus": {
            "ARI": "Direct and passionate in love. Attracted to challenge and excitement. Impulsive in romantic decisions.",
            "TAU": "Sensual and loyal in relationships. Values physical comfort and stability. Very determined in love.",
            "GEM": "Flirtatious and communicative. Needs mental stimulation in relationships. Enjoys variety in partners.",
            "CAN": "Nurturing and protective in love. Seeks emotional security. Very home and family oriented.",
            "LEO": "Dramatic and generous in relationships. Loves romance and admiration. Very proud in love.",
            "VIR": "Practical and discerning in love. Shows affection through service. Very attentive to details.",
            "LIB": "Harmonious and diplomatic. Seeks balance and partnership. Very artistic in expression of love.",
            "SCO": "Intense and passionate in relationships. Seeks deep emotional bonds. Very possessive in love.",
            "SAG": "Adventurous and freedom-loving. Values honesty in relationships. Philosophical about love.",
            "CAP": "Serious and responsible in love. Seeks stability and commitment. Very ambitious in relationships.",
            "AQU": "Unconventional and friendly. Values independence in relationships. Very innovative in love.",
            "PIS": "Romantic and compassionate. Seeks spiritual connection. Very dreamy in love."
        },
        "Mars": {
            "ARI": "Energetic and direct in sexual expression. Very competitive and pioneering. Quick to action.",
            "TAU": "Persistent and determined in sexuality. Very sensual and physical. Slow but steady approach.",
            "GEM": "Versatile and communicative in sexual expression. Enjoys variety and mental stimulation.",
            "CAN": "Protective and emotional in sexuality. Very nurturing and sensitive. Actions driven by feelings.",
            "LEO": "Confident and dramatic in sexual expression. Very creative and proud. Enjoys being center of attention.",
            "VIR": "Precise and analytical in sexuality. Very methodical and attentive to details.",
            "LIB": "Diplomatic and balanced in sexual expression. Seeks harmony and partnership.",
            "SCO": "Intense and transformative in sexuality. Very powerful and investigative. Seeks deep connections.",
            "SAG": "Adventurous and optimistic in sexual expression. Enjoys exploration and freedom.",
            "CAP": "Ambitious and disciplined in sexuality. Very strategic and patient. Seeks long-term goals.",
            "AQU": "Innovative and rebellious in sexual expression. Very unconventional and independent.",
            "PIS": "Compassionate and intuitive in sexuality. Very adaptable and inspired by feelings."
        }
    }

    # INTERPRETĂRI CARRIER
    career_interpretations = {
        "Sun": {
            "ARI": "Natural leader, entrepreneur, pioneer. Excels in competitive fields and startups.",
            "TAU": "Excellent in finance, real estate, agriculture. Builds lasting business structures.",
            "GEM": "Communicator, teacher, journalist. Thrives in media and information fields.",
            "CAN": "Nurturing careers: healthcare, hospitality, real estate. Strong business intuition.",
            "LEO": "Management, entertainment, creative arts. Natural performer and leader.",
            "VIR": "Healthcare, analysis, organization. Excellent with details and service.",
            "LIB": "Law, diplomacy, arts. Natural mediator and relationship builder.",
            "SCO": "Psychology, research, finance. Excellent in crisis management.",
            "SAG": "Education, travel, philosophy. Natural teacher and explorer.",
            "CAP": "Management, architecture, government. Builds lasting career structures.",
            "AQU": "Technology, innovation, social causes. Visionary and forward-thinking.",
            "PIS": "Arts, healing, spirituality. Creative and compassionate careers."
        },
        "Midheaven": {
            "ARI": "Career requires initiative and independence. Leadership roles suit you best.",
            "TAU": "Stable, secure careers with tangible results. Finance or building industries.",
            "GEM": "Communications, teaching, or multi-faceted careers that offer variety.",
            "CAN": "Careers involving nurturing, protection, or domestic matters.",
            "LEO": "Creative leadership roles where you can shine and receive recognition.",
            "VIR": "Service-oriented careers requiring attention to detail and analysis.",
            "LIB": "Partnership-based careers in law, arts, or diplomacy.",
            "SCO": "Careers involving transformation, research, or depth psychology.",
            "SAG": "Expansive careers involving travel, education, or philosophy.",
            "CAP": "Structured careers with clear hierarchy and long-term goals.",
            "AQU": "Innovative careers in technology, science, or social reform.",
            "PIS": "Creative or healing careers that allow spiritual expression."
        }
    }

    # INTERPRETĂRI RELATIONSHIPS
    relationships_interpretations = {
        "Venus": {
            "ARI": "Passionate and direct in relationships. Needs excitement and challenge.",
            "TAU": "Loyal and sensual partner. Values stability and physical connection.",
            "GEM": "Communicative and social. Needs mental stimulation in relationships.",
            "CAN": "Nurturing and protective. Seeks emotional security and family.",
            "LEO": "Generous and dramatic. Needs admiration and romance.",
            "VIR": "Practical and helpful. Shows love through service and attention.",
            "LIB": "Harmonious and partnership-oriented. Seeks balance and fairness.",
            "SCO": "Intense and transformative. Seeks deep, soul-level connections.",
            "SAG": "Adventurous and freedom-loving. Needs space and intellectual connection.",
            "CAP": "Responsible and committed. Builds relationships that last.",
            "AQU": "Independent and unconventional. Values friendship and mental connection.",
            "PIS": "Compassionate and spiritual. Seeks soulful, empathetic connections."
        },
        "Mars": {
            "ARI": "Direct and assertive in relationships. Needs action and initiative.",
            "TAU": "Persistent and determined. Slow to anger but very steadfast.",
            "GEM": "Communicative and versatile. Expresses desires through words.",
            "CAN": "Protective and emotional. Actions driven by deep feelings.",
            "LEO": "Confident and dramatic. Needs recognition and appreciation.",
            "VIR": "Analytical and precise. Very attentive to partner's needs.",
            "LIB": "Diplomatic and cooperative. Seeks harmony in interactions.",
            "SCO": "Intense and powerful. Very determined in pursuing desires.",
            "SAG": "Adventurous and optimistic. Needs freedom and expansion.",
            "CAP": "Ambitious and disciplined. Very responsible in commitments.",
            "AQU": "Innovative and independent. Unconventional in approach.",
            "PIS": "Compassionate and intuitive. Very adaptable and sensitive."
        }
    }

    # INTERPRETĂRI SPIRITUALE
    spiritual_interpretations = {
        "Sun": {
            "ARI": "Spiritual warrior. Learns courage and compassionate leadership.",
            "TAU": "Earth spirituality. Connects divine through nature and senses.",
            "GEM": "Messenger spirit. Integrates diverse knowledge and communication.",
            "CAN": "Nurturing spirit. Develops unconditional love and compassion.",
            "LEO": "Radiant spirit. Expresses creative divine energy.",
            "VIR": "Healing spirit. Sees sacredness in service and details.",
            "LIB": "Harmonious spirit. Masters balance and relationship wisdom.",
            "SCO": "Transformative spirit. Explores life-death-rebirth mysteries.",
            "SAG": "Seeker spirit. Explores philosophical and spiritual truth.",
            "CAP": "Mountain spirit. Builds spiritual structures and discipline.",
            "AQU": "Visionary spirit. Connects to collective consciousness.",
            "PIS": "Mystic spirit. Experiences unity and divine compassion."
        },
        "Neptune": {
            "ARI": "Inspired action and spiritual initiative.",
            "TAU": "Spiritual values and divine manifestation.",
            "GEM": "Inspired communication and spiritual learning.",
            "CAN": "Mystical emotions and spiritual home.",
            "LEO": "Visionary creativity and spiritual self-expression.",
            "VIR": "Spiritual service and healing work.",
            "LIB": "Idealized relationships and spiritual partnership.",
            "SCO": "Mystical transformation and spiritual depth.",
            "SAG": "Visionary beliefs and spiritual exploration.",
            "CAP": "Spiritual ambition and divine structure.",
            "AQU": "Inspired innovation and collective spirituality.",
            "PIS": "Divine compassion and spiritual unity."
        }
    }

    # SELECTEAZĂ SETUL CORESPUNZĂTOR
    if interpretation_type == "Natal":
        interpretations = natal_interpretations
    elif interpretation_type == "Sexual":
        interpretations = sexual_interpretations
    elif interpretation_type == "Career":
        interpretations = career_interpretations
    elif interpretation_type == "Relationships":
        interpretations = relationships_interpretations
    elif interpretation_type == "Spiritual":
        interpretations = spiritual_interpretations
    else:
        interpretations = natal_interpretations  # Fallback

    # AFIȘEAZĂ INTERPRETĂRILE PENTRU TOATE PLANETELE RELEVANTE
    planets_to_display = ["Sun", "Moon", "Mercury", "Venus", "Mars"]
    
    # Adaugă planete speciale în funcție de tipul de interpretare
    if interpretation_type == "Career":
        planets_to_display.append("Midheaven")
    elif interpretation_type == "Spiritual":
        planets_to_display.extend(["Neptune", "Jupiter"])
    elif interpretation_type == "Relationships":
        planets_to_display.extend(["Venus", "Mars"])  # Deja incluse, dar le accentuăm

    for planet_name in planets_to_display:
        if planet_name == "Midheaven":
            # Pentru Midheaven, folosim casa a 10-a
            planet_data = chart_data['houses'][10]
            planet_sign = planet_data['sign']
        elif planet_name in chart_data['planets']:
            planet_data = chart_data['planets'][planet_name]
            planet_sign = planet_data['sign']
        else:
            continue
            
        if (planet_name in interpretations and 
            planet_sign in interpretations[planet_name]):
            
            st.write(f"**** {planet_name}{planet_sign}")
            st.write(interpretations[planet_name][planet_sign])
            st.write("")
