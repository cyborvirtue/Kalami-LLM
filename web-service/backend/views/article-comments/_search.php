<?php

use yii\helpers\Html;
use yii\widgets\ActiveForm;

/** @var yii\web\View $this */
/** @var app\models\ArticleCommentsSearch $model */
/** @var yii\widgets\ActiveForm $form */
?>

<div class="article-comments-search">

    <?php $form = ActiveForm::begin([
        'action' => ['index'],
        'method' => 'get',
    ]); ?>

    <?= $form->field($model, 'CommentID') ?>

    <?= $form->field($model, 'UserID') ?>

    <?= $form->field($model, 'ArticleID') ?>

    <?= $form->field($model, 'Content') ?>

    <?= $form->field($model, 'CommentedAt') ?>

    <div class="form-group">
        <?= Html::submitButton('Search', ['class' => 'btn btn-primary']) ?>
        <?= Html::resetButton('Reset', ['class' => 'btn btn-outline-secondary']) ?>
    </div>

    <?php ActiveForm::end(); ?>

</div>
