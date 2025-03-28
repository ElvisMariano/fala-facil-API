# Generated by Django 5.1.7 on 2025-03-26 13:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Deck",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="nome")),
                ("description", models.TextField(blank=True, verbose_name="descrição")),
                (
                    "language",
                    models.CharField(
                        choices=[
                            ("en", "Inglês"),
                            ("es", "Espanhol"),
                            ("fr", "Francês"),
                            ("de", "Alemão"),
                            ("it", "Italiano"),
                            ("pt", "Português"),
                            ("ja", "Japonês"),
                            ("ko", "Coreano"),
                            ("zh", "Chinês"),
                            ("ru", "Russo"),
                        ],
                        max_length=2,
                        verbose_name="idioma",
                    ),
                ),
                (
                    "level",
                    models.CharField(
                        choices=[
                            ("A1", "Iniciante"),
                            ("A2", "Básico"),
                            ("B1", "Intermediário"),
                            ("B2", "Intermediário Superior"),
                            ("C1", "Avançado"),
                            ("C2", "Proficiente"),
                        ],
                        max_length=2,
                        verbose_name="nível",
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("vocabulary", "Vocabulário"),
                            ("grammar", "Gramática"),
                            ("pronunciation", "Pronúncia"),
                            ("expressions", "Expressões"),
                            ("conversation", "Conversação"),
                            ("reading", "Leitura"),
                            ("writing", "Escrita"),
                            ("listening", "Compreensão Auditiva"),
                        ],
                        max_length=20,
                        verbose_name="categoria",
                    ),
                ),
                (
                    "is_public",
                    models.BooleanField(
                        default=True,
                        help_text="Se marcado, o deck ficará visível para todos os usuários.",
                        verbose_name="público",
                    ),
                ),
                (
                    "is_featured",
                    models.BooleanField(
                        default=False,
                        help_text="Se marcado, o deck aparecerá na seção de destaques.",
                        verbose_name="destaque",
                    ),
                ),
                (
                    "is_archived",
                    models.BooleanField(
                        default=False,
                        help_text="Se marcado, o deck será arquivado e não aparecerá nas listagens.",
                        verbose_name="arquivado",
                    ),
                ),
                (
                    "tags",
                    models.CharField(
                        blank=True,
                        help_text="Tags separadas por vírgula.",
                        max_length=200,
                        verbose_name="tags",
                    ),
                ),
                (
                    "difficulty",
                    models.FloatField(
                        default=0.0,
                        help_text="Dificuldade média do deck (0.0 a 1.0).",
                        verbose_name="dificuldade",
                    ),
                ),
                (
                    "total_cards",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Total de cartões no deck.",
                        verbose_name="total de cartões",
                    ),
                ),
                (
                    "mastered_cards",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Total de cartões dominados pelos usuários.",
                        verbose_name="cartões dominados",
                    ),
                ),
                (
                    "average_mastery_time",
                    models.FloatField(
                        default=0.0,
                        help_text="Tempo médio para dominar os cartões (em dias).",
                        verbose_name="tempo médio de domínio",
                    ),
                ),
                (
                    "study_count",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Número de vezes que o deck foi estudado.",
                        verbose_name="contagem de estudos",
                    ),
                ),
                (
                    "favorite_count",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Número de usuários que favoritaram o deck.",
                        verbose_name="contagem de favoritos",
                    ),
                ),
                (
                    "share_count",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Número de vezes que o deck foi compartilhado.",
                        verbose_name="contagem de compartilhamentos",
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        default="#FFFFFF",
                        help_text="Cor do deck em formato hexadecimal.",
                        max_length=7,
                        verbose_name="cor",
                    ),
                ),
                (
                    "icon",
                    models.CharField(
                        default="book",
                        help_text="Nome do ícone do deck.",
                        max_length=50,
                        verbose_name="ícone",
                    ),
                ),
                (
                    "due_cards",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Número de cartões pendentes para revisão.",
                        verbose_name="cartões pendentes",
                    ),
                ),
                (
                    "last_studied_at",
                    models.DateTimeField(
                        blank=True,
                        default=None,
                        help_text="Data e hora do último estudo do deck.",
                        null=True,
                        verbose_name="último estudo",
                    ),
                ),
                (
                    "completion_rate",
                    models.FloatField(
                        default=0.0,
                        help_text="Taxa de conclusão do deck (0.0 a 1.0).",
                        verbose_name="taxa de conclusão",
                    ),
                ),
                (
                    "version",
                    models.CharField(
                        default="1.0.0",
                        help_text="Versão do deck no formato semântico.",
                        max_length=10,
                        verbose_name="versão",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="criado em")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="atualizado em")),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="decks",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="proprietário",
                    ),
                ),
                (
                    "parent_deck",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        help_text="Deck original em caso de cópia.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="derived_decks",
                        to="flashcards.deck",
                        verbose_name="deck original",
                    ),
                ),
            ],
            options={
                "verbose_name": "deck",
                "verbose_name_plural": "decks",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="DeckFavorite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="criado em")),
                (
                    "deck",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorites",
                        to="flashcards.deck",
                        verbose_name="deck",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorite_decks",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="usuário",
                    ),
                ),
            ],
            options={
                "verbose_name": "deck favorito",
                "verbose_name_plural": "decks favoritos",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Flashcard",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("front", models.TextField(verbose_name="frente")),
                ("back", models.TextField(verbose_name="verso")),
                ("example", models.TextField(blank=True, verbose_name="exemplo")),
                (
                    "audio",
                    models.FileField(
                        blank=True, null=True, upload_to="flashcards/audio/", verbose_name="áudio"
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="flashcards/images/", verbose_name="imagem"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="criado em")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="atualizado em")),
                (
                    "deck",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="flashcards",
                        to="flashcards.deck",
                        verbose_name="deck",
                    ),
                ),
            ],
            options={
                "verbose_name": "flashcard",
                "verbose_name_plural": "flashcards",
                "ordering": ["deck", "created_at"],
            },
        ),
        migrations.CreateModel(
            name="FlashcardProgress",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("correct_attempts", models.IntegerField(default=0)),
                ("incorrect_attempts", models.IntegerField(default=0)),
                ("average_response_time", models.FloatField(default=0)),
                ("last_reviewed", models.DateTimeField(null=True)),
                ("next_review_date", models.DateTimeField(null=True)),
                ("ease_factor", models.FloatField(default=2.5)),
                ("interval", models.IntegerField(default=1)),
                ("streak", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "flashcard",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="flashcards.flashcard"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                "ordering": ["next_review_date"],
            },
        ),
        migrations.AddIndex(
            model_name="deck",
            index=models.Index(fields=["language"], name="flashcards__languag_e02297_idx"),
        ),
        migrations.AddIndex(
            model_name="deck",
            index=models.Index(fields=["level"], name="flashcards__level_d01d4d_idx"),
        ),
        migrations.AddIndex(
            model_name="deck",
            index=models.Index(fields=["category"], name="flashcards__categor_bf2ec8_idx"),
        ),
        migrations.AddIndex(
            model_name="deck",
            index=models.Index(fields=["owner"], name="flashcards__owner_i_3fb753_idx"),
        ),
        migrations.AddIndex(
            model_name="deck",
            index=models.Index(fields=["created_at"], name="flashcards__created_15643e_idx"),
        ),
        migrations.AddIndex(
            model_name="deck",
            index=models.Index(fields=["is_public"], name="flashcards__is_publ_c5ae3e_idx"),
        ),
        migrations.AddIndex(
            model_name="deck",
            index=models.Index(fields=["is_featured"], name="flashcards__is_feat_5f16d3_idx"),
        ),
        migrations.AddIndex(
            model_name="deck",
            index=models.Index(fields=["is_archived"], name="flashcards__is_arch_e3a207_idx"),
        ),
        migrations.AddIndex(
            model_name="deck",
            index=models.Index(fields=["difficulty"], name="flashcards__difficu_68350d_idx"),
        ),
        migrations.AddIndex(
            model_name="deck",
            index=models.Index(fields=["study_count"], name="flashcards__study_c_d3ef89_idx"),
        ),
        migrations.AddIndex(
            model_name="deck",
            index=models.Index(fields=["favorite_count"], name="flashcards__favorit_4445ff_idx"),
        ),
        migrations.AddIndex(
            model_name="deck",
            index=models.Index(fields=["due_cards"], name="flashcards__due_car_1c2363_idx"),
        ),
        migrations.AddIndex(
            model_name="deck",
            index=models.Index(fields=["last_studied_at"], name="flashcards__last_st_3e7c1d_idx"),
        ),
        migrations.AddIndex(
            model_name="deck",
            index=models.Index(fields=["completion_rate"], name="flashcards__complet_b25f6c_idx"),
        ),
        migrations.AddIndex(
            model_name="deck",
            index=models.Index(fields=["version"], name="flashcards__version_b2793a_idx"),
        ),
        migrations.AddIndex(
            model_name="deckfavorite",
            index=models.Index(fields=["user"], name="flashcards__user_id_c2dd56_idx"),
        ),
        migrations.AddIndex(
            model_name="deckfavorite",
            index=models.Index(fields=["deck"], name="flashcards__deck_id_ab23b8_idx"),
        ),
        migrations.AddIndex(
            model_name="deckfavorite",
            index=models.Index(fields=["created_at"], name="flashcards__created_792fb6_idx"),
        ),
        migrations.AlterUniqueTogether(
            name="deckfavorite",
            unique_together={("user", "deck")},
        ),
        migrations.AddIndex(
            model_name="flashcardprogress",
            index=models.Index(fields=["user"], name="flashcards__user_id_c41458_idx"),
        ),
        migrations.AddIndex(
            model_name="flashcardprogress",
            index=models.Index(fields=["flashcard"], name="flashcards__flashca_bbcf98_idx"),
        ),
        migrations.AddIndex(
            model_name="flashcardprogress",
            index=models.Index(fields=["next_review_date"], name="flashcards__next_re_65721e_idx"),
        ),
        migrations.AlterUniqueTogether(
            name="flashcardprogress",
            unique_together={("user", "flashcard")},
        ),
    ]
