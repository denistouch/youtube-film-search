from matcher import match_candidate_to_candidates


def test():
    cases = {
        'candidate': 'Шазам (2019)',
        'candidates': ['Шазам! (2019)', 'Седьмой пробег по контуру Земного шара (2019)', 'Шаман (2019)',
                       'Шалом, Тайвань (2019)',
                       'Ток-шоу Моны Эль Шазли (2019)', 'Шазам! (1974)', 'Шазам! (2013)',
                       'Шазам! Ярость богов (2023)',
                       'Шазам и Потерянный путь (2013)',
                       'Витрина DC: Супермен/Шазам! – Возвращение черного Адама (2010)'],
        'threshold': 50
    }
    answer, score = match_candidate_to_candidates(cases['candidate'], cases['candidates'], cases['threshold'])
    a = 1


if __name__ == '__main__':
    test()
