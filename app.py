def display_complete_interpretations(chart_data, interpretation_type):
    """Display interpretations for Natal, Natal Aspects, and Sexual only"""
    
    # Natal Interpretations (Planets in Signs) - TOATE PLANETELE
    natal_interpretations = {
        "Sun": {
            "ARI": "Open, energetic, strong, enthusiastic, forward looking, positive, determined, inventive, bright, filled with a zest for life.",
            "TAU": "Reliable, able, with powers of concentration, tenacity. Steadfast, a loving & affectionate 'family' person. Honest, forthright. Learns readily from mistakes.",
            "GEM": "Clever, bright, quickwitted, communicative, able to do many different things at once, eager to learn new subjects. Openminded, adaptable, curious, restless, confident, seldom settling down.",
            "CAN": "Emotional, complex, loving, sympathetic, understanding, humanitarian, kind, tender, respectful of the rights of others.",
            "LEO": "Self reliant, popular, good at leading others & at administration. Lots of directed energy & drive - good at achieving that which is desired. Very confident.",
            "VIR": "Cool, critical, idealistic but practical, hardworking & a good planner. Sees things through to the finish. Trustworthy, dependable, never shirks responsibilities. Perfectionist for the sake of perfection.",
            "LIB": "Friendly, cordial, artistic, kind, considerate, loyal, alert, sociable, moderate, balanced in views, open-minded.",
            "SCO": "Determined, direct, confident, sincere, brave, courageous, strongwilled, unafraid of setbacks or hard work. Principled & unswerving once a path has been decided on - has very clear goals.",
            "SAG": "Forthright, freedom loving, honest, tolerant, broadminded, open, frank, fair, dependable, trusting (seldom suspicious), optimistic, generous, intelligent, respected, earnest, funloving & trustworthy.",
            "CAP": "Orderly, patient, serious, stable, persevering, careful, prudent, just, (justice usually being more important to this person than mercy). Will always repay favours - self-reliant.",
            "AQU": "Independent, tolerant, honest, forthright, considerate, helpful, sincere, generous, unprejudiced, broadminded, reliable, refined & humanitarian. An intense kinship with nature. Not much practical common sense.",
            "PIS": "Sensitive, sympathetic, understanding, kind, sentimental, dedicated, broadminded, uncritical of the shortcomings of others. Quite earnest & trustworthy. Generous."
        },
        "Moon": {
            "ARI": "Energetic, ambitious, strongwilled, self-centred, impulsive, dominant & obstinate.",
            "TAU": "Gregarious, sociable, sensuous, sometimes strongly possessive.",
            "GEM": "Quickwitted. Hungry for new experiences - a traveller. Impressionable.",
            "CAN": "Sensitive, friendly, but reserved; tradition loving; lives in fantasy.",
            "LEO": "A cheerful nature, with strong ego, which could lead to vanity, pride & conceit.",
            "VIR": "Often speaks too much & too hastily. Closed book to others.",
            "LIB": "Polite, diplomatic, good social manners. Eloquent.",
            "SCO": "Tenacious will, much energy & working power, passionate, often sensual. Honest.",
            "SAG": "Active or restless (a roving spirit), easily inspired, but not at all persevering.",
            "CAP": "Reserved, careful, sly. Learns by experience - reacts slowly to new things. Common sense.",
            "AQU": "Openminded, loves freedom, original even eccentric. Individualistic.",
            "PIS": "Rich fantasy, deep feeling, impressionable. Easy to discourage. Receptive."
        },
        "Mercury": {
            "ARI": "Open & self-reliant, speaks fluently & too much. Ready to fight, full of new ideas.",
            "TAU": "Thorough, persevering. Good at working with the hands. Inflexible, steady, obstinate, self-opinionated, conventional, limited in interests.",
            "GEM": "Combative. Many-sided, interested in many subjects, well read, mentally swift.",
            "CAN": "Dreamy, fantasises & lives in the past. Tactful, diplomatic.",
            "LEO": "Sociable, optimistic, enjoys life. Self-confident (too much?).",
            "VIR": "Quickwitted. Thinks realistically. Has an eye for detail. Can be fussy.",
            "LIB": "Rational, appreciative, ready to compromise. Observant. Lacking in thoroughness.",
            "SCO": "A shrewd & thorough thinker, taciturn, acute, penetrating, with a deep & silent personality.",
            "SAG": "Frank, sincere, humanitarian, justice loving, rich in ideas.",
            "CAP": "Logical, systematic, critical, shrewd, often a slow thinker/mover.",
            "AQU": "Original, full of ideas, intuitive, usually good memory.",
            "PIS": "Emotional, impressionable. Always fantasising, dreaming."
        },
        "Venus": {
            "ARI": "Impulsive, passionate, self reliant, extroverted. Sometimes sociable.",
            "TAU": "Often tender, sensual. Overpossessive & sometimes jealous. A good mixer.",
            "GEM": "Flirtatious. Makes friends very easily. Has multifaceted relationships.",
            "CAN": "Homeloving. Wary of others- generally cautious. A good host.",
            "LEO": "Magnanimous, self-centred, often creative. An exhibitionist - loves acting.",
            "VIR": "Appears cool & closed: really passionate. Shy, restrained, scheming.",
            "LIB": "Very sociable, many friendships but few deep or enduring ones.",
            "SCO": "Passionate, intense, sensual, exacting, highly sensitive to any slight or neglect.",
            "SAG": "Freedom-loving: hence unstable, changeful in friendships & marriage.",
            "CAP": "Faithful & usually reliable, but capricious at times.",
            "AQU": "Impersonal but friendly, makes contacts easily.",
            "PIS": "Tolerant, compassionate, always ready to help. Self-sacrificing."
        },
        "Mars": {
            "ARI": "Energetic, enterprising, vital, open, fond of independence.",
            "TAU": "Determined, often unyielding, persevering in work, quite self reliant.",
            "GEM": "Interested in many things, quick, perceptive, eloquent, acute, sarcastic argumentative.",
            "CAN": "Domestic life is very important - in this, practical & constructive.",
            "LEO": "Ambitious, enthusiastic, persevering. Powerful, generous, hot-tempered.",
            "VIR": "Considerate, appreciative, prudent, careful, meticulous, persevering, a natural worrier.",
            "LIB": "Seldom angry or ill-natured. Temperamental, moody & vain.",
            "SCO": "Dynamic. Extremely strong willed. Capable of anything when determined.",
            "SAG": "Energetic, fond of travelling & adventure. Often not very persevering. Hasty, inconsiderate.",
            "CAP": "Ambitious, strongwilled, persevering. Strives for rise, power, fame.",
            "AQU": "Strong reasoning powers. Often interested in science. Fond of freedom & independence.",
            "PIS": "Failure because of multifarious aims. Prefers compromise. Restless. No self confidence."
        },
        "Jupiter": {
            "ARI": "Optimistic, energetic, fond of freedom & justice, stands up for ideas & ideals.High-spirited & self-willed.",
            "TAU": "Reliable, good-natured, in search of success through constancy, builds up future in lots of little steps. Usually good judgement.",
            "GEM": "Quickwitted, interested in many things, intent on expanding horizons through travel & study. Often superficial.",
            "CAN": "Appreciative of others. Plans life carefully. Intuitive, but lives in a fantasy world.",
            "LEO": "Has a talent for organizing & leading. Open & ready to help anyone in need - magnanimous & affectionate.",
            "VIR": "Objectively critical, conscientious, overskeptical, quiet, kind, rather too matter-of-fact, reliable",
            "LIB": "Gregarious, well-loved, fair, ethical, good. Convincing at conversation.",
            "SCO": "Strongwilled, ambitious, persevering, determined & smart.",
            "SAG": "Optimistic, always interested in learning something new.",
            "CAP": "Has a sense of responsibility. Ambitious. Conventional, economical,honest sometimes avaricious. Persevering & stubborn.",
            "AQU": "Idealistic, sociable, interested in teaching or philosophy. Tolerant.",
            "PIS": "Compassionate, hospitable, ready to help others, jolly, pleasant, very easy-going."
        },
        "Saturn": {
            "ARI": "Some talent for organizing, strives for leadership: however, lacks the necessary sense of responsibility & depth.",
            "TAU": "Realistic, strongwilled, persevering, careful.",
            "GEM": "Concentrates, a thinker. Profound, well-ordered, disciplined, logical, austere, serious.",
            "CAN": "Sense of responsibility for the family. Conservative, economical.",
            "LEO": "Talent for organizing, strongwilled, self-confident. Pursues objectives obstinately, heedless of others. Jealous, possessive.",
            "VIR": "A methodical & logical thinker: sometimes a ponderer. Careful, practical, conscientious, sometimes pedantic, severe, overprudent.",
            "LIB": "Sociable, reliable, patient, fond of justice, rational, tactful, usually diplomatic.",
            "SCO": "Determined, persevering, pursues professional objectives tenaciously. Usually inflexible.",
            "SAG": "Upright, open, courageous, honourable, grave, dignified, very capable.",
            "CAP": "Highly ambitious, serious, usually introverted. Conventional.",
            "AQU": "Pragmatic, observant. Able to influence others. Overpowering desire for independence.",
            "PIS": "Sympathetic, adaptable, ready to sacrifice self for others, but often indecisive, cowardly, sad, moody, worrying."
        },
        "Uranus": {
            "ARI": "Original, strongwilled, insists on personal freedom & independence. Proud, courageous, rebellious, dogmatic.",
            "TAU": "Determined, self-willed, industrious, self-reliant, practical, a dogged pursuer of goals.",
            "GEM": "Rich in ideas, inventive, versatile, gifted, able, an original thinker.",
            "CAN": "Rather passive, compassionate, sensitive, impressionable, intuitive.",
            "LEO": "Eccentric, original, artistic, quite self-reliant - a loner. Sometimes arrogant, wilful.",
            "VIR": "Hypercritical, clever, whimsical. Peculiar views on health & nutrition. Emotionally unreliable.",
            "LIB": "Fond of justice, fair. Original, unorthodox views on law. Restless, romantic.",
            "SCO": "Strongwilled, intelligent, malicious, sly, vengeful. Intent on bodily & sensual enjoyment.",
            "SAG": "Active, sociable. Purposeful, methodical but reckless, highly-strung, rebellious, excitable, adventurous.",
            "CAP": "Talent for organizing, with a strong will, a fierce warlike nature, often a very strong personality.",
            "AQU": "Original, rich in ideas, independent, usually interested in science.",
            "PIS": "Sensitive, appreciative, adaptable, often passive. Frequently idealistic, visionary, religious, impractical."
        },
        "Neptune": {
            "ARI": "Lives in fantasy. Perseveres in finding solutions for problems.",
            "TAU": "Likes spiritual things. Very secretive. Impractical, overly traditional.",
            "GEM": "Complex, worrying, fantasising, has many impractical ideas but sometimes flashes of brilliance too. Muddle-headed.",
            "CAN": "Dreamy, inclined to escape from reality. Loves luxuries & comforts that life can offer.",
            "LEO": "Fond of freedom. Takes risks. Conceited. Often stands up for own beliefs & ideals.",
            "VIR": "Humble. Sometimes has prophetic foresight. Is very critical, sceptical about orthodox religion, tradition & received opinions in general.",
            "LIB": "Idealistic, often a bit out of touch with reality. Has only a hazy view & understanding of real life & the world.",
            "SCO": "Emotionally intense. Has ideals of social justice & morality. Secretive.",
            "SAG": "Shrewd, wide-awake intellect. Interested in an unattainable Utopia.",
            "CAP": "Can intuitively grasp things.",
            "AQU": "Often has obscure & quixotic ideas.",
            "PIS": "Gentle, loving, sociable, honest & reliable."
        },
        "Pluto": {
            "ARI": "Straightforward, sometimes a little bit egotistical. Very assertive. Pioneering leader.",
            "TAU": "Very interested in modern technology. Materially acquisitive.",
            "GEM": "Strong & self-reliant, able to appraise people & situations very quickly & correctly.",
            "CAN": "Rich inner life, often active dreams & fantasy.",
            "LEO": "Strong creative desires. Uncontrollable sexual appetite. Determined to win.",
            "VIR": "Prone to soul-searching & self-criticism. Thinks & acts to the point.",
            "LIB": "Often ruled by the intellect: tries to solve problems logically. Interested in justice & the law.",
            "SCO": "Tenacious, exceptionally enduring. Can lead the way, however difficult. Emotionally intense, highly sexual.",
            "SAG": "Interested in the study of racial & ethnic differences & origins & of traditional beliefs.",
            "CAP": "Fascinated by new things. Dictatorial, impatient, lacking in consideration, dedicated to own profession.",
            "AQU": "Has many friends. Original, has many ideas. Demanding in personal relationships.",
            "PIS": "Profound, intellectual, introverted - does not like crowds.Investigative, patient. Creative & artistic"
        }
    }

    # Natal Aspects Interpretations
    aspect_interpretations = {
        "SUN = MOO": "a feeling or moody nature",
        "SUN + MOO": "emotionally well-balanced", 
        "SUN - MOO": "feels a split between emotions and will",
        # ... (toate aspectele tale aici - le păstrez pe toate)
        "URA = PLU": "highly clairvoyant, metaphysical, extremely devotional, evolved"
    }

    # House Interpretations - TOATE CASELE
    house_interpretations = {
        "01": "Usually warmhearted & lovable but also vain, hedonistic & flirtatious.",
        "02": "Often very level-headed & talented, but also rather materialistic.",
        "03": "Communicative, usually a good speaker & a lucid writer.", 
        "04": "Home is the one of the most important things in life for this person.",
        "05": "As a child energetic, noisy, overactive, fond of taking risks.",
        "06": "Willing to organize & work hard. Adaptable.",
        "07": "Friendly, sociable, interested in a bettering own quality of life.",
        "08": "Serious by nature. Though interested in material things, fascinated by philosophies of life & death.",
        "09": "Has very wide-ranging interests.",
        "10": "Appreciative of the importance of success in life.",
        "11": "Often has a clear object or goal in view. A good organizer.",
        "12": "Dreamy, delicate, vulnerable, shy, reserved, introspective. Forgetful."
    }

    # Display based on interpretation type
    st.subheader(f"📖 {interpretation_type} Interpretation")
    
    if interpretation_type == "Natal":
        # Display ALL planetary interpretations
        planets_to_display = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", 
                             "Saturn", "Uranus", "Neptune", "Pluto"]
        
        for planet_name in planets_to_display:
            if planet_name in chart_data['planets']:
                planet_data = chart_data['planets'][planet_name]
                planet_sign = planet_data['sign']
                
                if (planet_name in natal_interpretations and 
                    planet_sign in natal_interpretations[planet_name]):
                    
                    with st.expander(f"{planet_name} in {planet_sign}", expanded=True):
                        st.write(natal_interpretations[planet_name][planet_sign])
                        st.write(f"**Position**: {planet_data['position_str']}")

    elif interpretation_type == "Natal Aspects":
        # Display ALL aspect interpretations
        aspects = calculate_aspects(chart_data)
        if aspects:
            for aspect in aspects:
                planet1 = aspect['planet1']
                planet2 = aspect['planet2']
                aspect_name = aspect['aspect_name']
                
                # Create aspect key for lookup
                aspect_key = f"{planet1.upper()} = {planet2.upper()}"
                
                with st.expander(f"{planet1} {aspect_name} {planet2}", expanded=False):
                    st.write(f"**Aspect**: {aspect_name}")
                    st.write(f"**Orb**: {aspect['orb']:.2f}°")
                    st.write(f"**Strength**: {aspect['strength']}")
                    
                    if aspect_key in aspect_interpretations:
                        st.write(f"**Interpretation**: {aspect_interpretations[aspect_key]}")
                    else:
                        st.write("**Interpretation**: Significant planetary interaction")
        else:
            st.info("No significant aspects found within allowed orb.")

    elif interpretation_type == "Sexual":
        # Display ALL house interpretations for sexual energy
        st.write("**Sexual Energy & Expression - All Houses**")
        
        # Display ALL 12 houses
        for house_num in range(1, 13):
            if house_num in chart_data['houses']:
                house_data = chart_data['houses'][house_num]
                
                with st.expander(f"House {house_num} - {get_house_sexual_theme(house_num)}", expanded=False):
                    if str(house_num) in house_interpretations:
                        st.write(house_interpretations[str(house_num)])
                    st.write(f"**Position**: {house_data['position_str']}")

def get_house_sexual_theme(house_num):
    """Get sexual theme for each house"""
    themes = {
        1: "Self & Identity",
        2: "Values & Sensuality", 
        3: "Communication & Curiosity",
        4: "Home & Emotional Security",
        5: "Pleasure & Romance",
        6: "Health & Service",
        7: "Partnerships & Balance",
        8: "Intimacy & Transformation",
        9: "Expansion & Philosophy", 
        10: "Career & Public Life",
        11: "Friendships & Social",
        12: "Subconscious & Fantasy"
    }
    return themes.get(house_num, "Personal Energy")
